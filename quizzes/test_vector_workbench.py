import copy
import json
import tempfile
from fractions import Fraction
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .models import Question, Quiz, UserQuestionProgress
from .mode_services import build_training_payload
from .seed_loader import SeedValidationError, _validate_quiz_payload, load_quiz_file
from .vector_workbench import (MODE_KEYS, VectorValidationError, check_answer, number,
                               public_config, solved_values, validate_config)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = json.loads((ROOT/'docs/vectori_in_plan_interactive.examples.json').read_text(encoding='utf-8'))['examples']


def config(example):
    return {key: copy.deepcopy(example[key]) for key in MODE_KEYS[example['mode']] | {'mode'}}


def answer(example):
    result = copy.deepcopy(example['expected'])
    if example['mode'] == 'head_to_tail':
        result['tail'] = list(example['u'])
    return result


def payload(example):
    return {'title':'Vector test fixture', 'difficulty':'medium', 'questions':[
        {'text':example['prompt'], 'type':'vector_workbench','format':'interactive',
         'points':10,'explanation':'Exact fixture explanation','interactive':config(example)}]}


class VectorMathTests(SimpleTestCase):
    def test_all_twelve_independently_specified_answers(self):
        self.assertEqual(len(EXAMPLES), 12)
        for example in EXAMPLES:
            with self.subTest(example=example['id']):
                data = config(example)
                self.assertTrue(check_answer(data, answer(example)))
                self.assertTrue(check_answer(data, solved_values(data)))
                self.assertEqual(public_config(data), data)

    def test_wrong_answers_in_every_mode_are_rejected(self):
        for example in EXAMPLES:
            values = answer(example)
            if 'selected' in values:
                values['selected'] = []
            elif 'relation' in values:
                values['relation'] = 'equal'
            else:
                key = 'coefficients' if 'coefficients' in values else next(k for k in values if k != 'tail')
                values[key][0] = str(Fraction(str(values[key][0])) + 1)
            with self.subTest(example=example['id']):
                self.assertFalse(check_answer(config(example), values))

    def test_head_to_tail_requires_actual_transport_even_with_correct_result(self):
        example = next(e for e in EXAMPLES if e['id']=='V07')
        values = answer(example)
        values['tail'] = [0,0]
        self.assertFalse(check_answer(config(example),values))
        del values['tail']
        with self.assertRaises(VectorValidationError):
            check_answer(config(example),values)

    def test_fraction_and_romanian_numeric_notation_is_exact(self):
        for raw, expected in [('−2/3',Fraction(-2,3)),('0,5',Fraction(1,2)),
                              ('1.5 / -0.5',Fraction(-3)),('.25',Fraction(1,4))]:
            self.assertEqual(number(raw),expected)
        values = {'coefficients':['4/3','−2/3']}
        self.assertTrue(check_answer(config(EXAMPLES[-1]), values))

    def test_malformed_and_unbounded_numeric_values(self):
        for raw in [True, False, None, {}, [], 'NaN',float('nan'),float('inf'),
                    '1e6','1/0','1 / 0.0','9'*65,' '*100+'1','1/1000001','1000001']:
            with self.subTest(raw=repr(raw)), self.assertRaises(VectorValidationError):
                number(raw)

    def test_config_rejects_unknown_keys_missing_points_and_collinear_basis(self):
        base = config(EXAMPLES[0])
        for key in ['expected','answers','solution','endpoint']:
            data = copy.deepcopy(base);data[key] = [3,2]
            with self.subTest(key=key),self.assertRaises(VectorValidationError):
                validate_config(data)
        data = config(EXAMPLES[-1]);data['v'] = [12,6]
        with self.assertRaises(VectorValidationError): validate_config(data)
        data = copy.deepcopy(base);data['reference'] = ['A','NotPresent']
        with self.assertRaises(VectorValidationError): validate_config(data)
        data = config(EXAMPLES[1]);data['points']['B'] = data['points']['A']
        with self.assertRaises(VectorValidationError): validate_config(data)
        data = {'mode':'scale_vector','u':[1000000,1],'scalar':1000000}
        with self.assertRaises(VectorValidationError): validate_config(data)

    def test_answers_reject_extra_keys_forged_config_duplicate_selection(self):
        for example in EXAMPLES:
            for extra in ['mode','interactive','expected','is_correct','user_id']:
                values = answer(example);values[extra] = 'forged'
                with self.subTest(example=example['id'],extra=extra),self.assertRaises(VectorValidationError):
                    check_answer(config(example),values)
        data = config(EXAMPLES[0])
        for value in [None, {}, {'selected':['CD','CD']},{'selected':['ZZ']},{'selected':{'CD':True}}]:
            with self.assertRaises(VectorValidationError):check_answer(data,value)

    def test_zero_scalar_is_valid_and_has_no_artificial_direction(self):
        self.assertTrue(check_answer({'mode':'scale_vector','u':[3,2],'scalar':0},{'vector':[0,0]}))
        self.assertTrue(check_answer({'mode':'scale_vector','u':[0,0],'scalar':-2},{'vector':[0,0]}))

    def test_loader_accepts_all_modes_and_rejects_injected_keys(self):
        for example in EXAMPLES:
            data = payload(example)
            _validate_quiz_payload(data,'fixture.json')
            data['questions'][0]['interactive']['expected'] = example['expected']
            with self.subTest(example=example['id']),self.assertRaises(SeedValidationError):
                _validate_quiz_payload(data,'fixture.json')


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'], ANALYTICS_ENABLED=False)
class VectorEndpointTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('vector-student')
        cls.other = get_user_model().objects.create_user('vector-other')
        cls.quiz = Quiz.objects.create(title='Vector fixture',difficulty='medium')
        cls.questions = []
        for index, example in enumerate(EXAMPLES):
            cls.questions.append(Question.objects.create(quiz=cls.quiz,order=index,text=example['prompt'],
                question_type=Question.TYPE_VECTOR_WORKBENCH, format_tag=Question.FORMAT_INTERACTIVE,
                explanation='SECRET SOLUTION '+example['id'],interactive_data=config(example)))

    def setUp(self):
        self.client.force_login(self.user)

    def post(self, question, values, **extra):
        return self.client.post(reverse('training_submit',args=[self.quiz.pk]),
            {'question_id':question.pk,'values':json.dumps(values),**extra})

    def test_all_modes_save_verified_progress_and_return_explanation(self):
        for question, example in zip(self.questions,EXAMPLES):
            with self.subTest(example=example['id']):
                response = self.post(question,answer(example))
                self.assertEqual(response.status_code,200)
                self.assertTrue(response.json()['is_correct'])
                self.assertEqual(response.json()['explanation'],question.explanation)
                progress = UserQuestionProgress.objects.get(user=self.user,question=question)
                self.assertEqual(progress.training_status,'correct')

    def test_unsolved_payload_hides_solution_and_solved_refresh_shows_exact_construction(self):
        before = build_training_payload(self.user,self.quiz,0,'/submit/')
        for question in before['questions']:
            self.assertNotIn('solvedValues',question)
            self.assertEqual(question['explanation'],'')
            self.assertNotIn('answers',question['interactive'])
            self.assertNotIn('expected',question['interactive'])
        for question,example in zip(self.questions,EXAMPLES):self.post(question,answer(example))
        after = build_training_payload(self.user,self.quiz,0,'/submit/')
        for question,example in zip(after['questions'],EXAMPLES):
            self.assertTrue(check_answer(config(example),question['solvedValues']))
            self.assertTrue(question['explanation'])

    def test_wrong_answer_stays_wrong_without_explanation_or_solved_values(self):
        response = self.post(self.questions[0],{'selected':[]})
        self.assertEqual(response.status_code,200)
        self.assertFalse(response.json()['is_correct'])
        self.assertEqual(response.json()['explanation'],'')
        item = build_training_payload(self.user,self.quiz,0,'/submit/')['questions'][0]
        self.assertEqual(item['status'],'wrong')
        self.assertNotIn('solvedValues',item)

    def test_malformed_and_forged_values_return_400_without_saving(self):
        for values in [None,[],{}, {'selected':['ZZ']}, {'selected':['CD'],'is_correct':True}]:
            with self.subTest(values=values):
                self.assertEqual(self.post(self.questions[0],values).status_code,400)
        url = reverse('training_submit',args=[self.quiz.pk])
        self.assertEqual(self.client.post(url,{'question_id':self.questions[0].pk,'values':'{broken'}).status_code,400)
        self.assertFalse(UserQuestionProgress.objects.filter(user=self.user).exists())

    def test_authentication_and_question_topic_membership(self):
        self.client.logout()
        self.assertEqual(self.post(self.questions[0],answer(EXAMPLES[0])).status_code,302)
        self.client.force_login(self.user)
        foreign_quiz = Quiz.objects.create(title='Foreign topic')
        foreign = Question.objects.create(quiz=foreign_quiz,text='Foreign',question_type=Question.TYPE_VECTOR_WORKBENCH,
                                          interactive_data=config(EXAMPLES[0]))
        self.assertEqual(self.post(foreign,answer(EXAMPLES[0])).status_code,404)

    def test_user_id_cannot_redirect_saved_progress_to_another_user(self):
        other_progress = UserQuestionProgress.objects.create(user=self.other,question=self.questions[0],training_status='wrong')
        response = self.post(self.questions[0],answer(EXAMPLES[0]),user_id=self.other.pk)
        self.assertEqual(response.status_code,200)
        other_progress.refresh_from_db()
        self.assertEqual(other_progress.training_status,'wrong')
        self.client.force_login(self.other)
        item = build_training_payload(self.other,self.quiz,0,'/submit/')['questions'][0]
        self.assertNotIn('solvedValues',item)

    def test_repeat_import_preserves_ids_options_and_saved_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'vector_fixture.json'
            path.write_text(json.dumps(payload(EXAMPLES[0])),encoding='utf-8')
            quiz,_ = load_quiz_file(path)
            question = quiz.questions.get()
            saved = UserQuestionProgress.objects.create(user=self.user,question=question,training_status='correct')
            load_quiz_file(path);load_quiz_file(path)
            saved.refresh_from_db()
            self.assertEqual(quiz.questions.get().pk,question.pk)
            self.assertEqual(saved.training_status,'correct')
