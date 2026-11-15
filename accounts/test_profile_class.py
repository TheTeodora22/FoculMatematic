from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.forms import ProfileEditForm
from accounts.services import get_profile_dashboard
from quizzes.learning import get_next_learning_step


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ProfileClassTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('profile-class-test')
        self.client.force_login(self.user)

    def test_new_profile_has_a_supported_class_and_working_link(self):
        self.assertEqual(self.user.profile.clasa, 5)
        dashboard = get_profile_dashboard(self.user)
        self.assertEqual(self.client.get(dashboard['class_url']).status_code, 200)

    def test_legacy_invalid_class_opens_selection_without_changing_stored_class(self):
        profile = self.user.profile
        for value in [1, 0, 13]:
            profile.clasa = value
            profile.save(update_fields=['clasa'])
            dashboard = get_profile_dashboard(self.user)
            self.assertEqual(dashboard['class_url'], reverse('profile_edit'))
            self.assertEqual(get_next_learning_step(self.user)['url'], reverse('profile_edit'))
            self.assertEqual(self.client.get(dashboard['class_url']).status_code, 200)
            response = self.client.get(reverse('profile'))
            self.assertContains(response, 'Alege clasa')
            profile.refresh_from_db()
            self.assertEqual(profile.clasa, value)

    def test_editor_rejects_unsupported_classes(self):
        for value in [1, 0, 13]:
            form = ProfileEditForm(data={'clasa':value, 'avatar':'default_avatar', 'theme':'light'},
                                   instance=self.user.profile, user=self.user)
            self.assertFalse(form.is_valid())
            self.assertIn('clasa', form.errors)

    def test_selecting_class_restores_class_link(self):
        response = self.client.post(reverse('profile_edit'),
            {'clasa':9, 'avatar':'default_avatar', 'theme':'light'})
        self.assertRedirects(response, reverse('profile'))
        self.user.profile.refresh_from_db()
        dashboard = get_profile_dashboard(self.user)
        self.assertEqual(dashboard['class_url'], reverse('class_chapters', args=[9]))
        self.assertEqual(self.client.get(dashboard['class_url']).status_code, 200)
