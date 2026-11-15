/* Progressive enhancements for navigation and ordinary account/report forms.
   Exercise forms and their persistence handlers are intentionally separate. */
(function () {
    'use strict';
    document.documentElement.classList.add('fm-ui-ready');
    document.querySelectorAll('[data-reload-page]').forEach(button => {
        button.addEventListener('click', () => window.location.reload());
    });

    const header = document.querySelector('.site-header');
    let compact = false;
    function updateHeader() {
        // Hysteresis prevents flicker near the compact threshold.
        if (!header) return;
        if (window.scrollY > 80) compact = true;
        else if (window.scrollY < 24) compact = false;
        header.classList.toggle('is-compact', compact);
    }
    window.addEventListener('scroll', updateHeader, {passive: true});
    updateHeader();

    const dropdowns = [...document.querySelectorAll('.nav__link .has-submenu')];
    function setDropdown(item, open) {
        item.classList.toggle('is-open', open);
        item.querySelector('.nav-dropdown-toggle').setAttribute('aria-expanded', String(open));
        item.querySelector('.submenu').inert = !open;
    }
    function closeDropdowns(except) {
        dropdowns.forEach(item => { if (item !== except) setDropdown(item, false); });
    }
    dropdowns.forEach(item => {
        const toggle = item.querySelector('.nav-dropdown-toggle');
        const menu = item.querySelector('.submenu');
        setDropdown(item, false);
        toggle.addEventListener('click', () => {
            const open = !item.classList.contains('is-open');
            closeDropdowns(item);
            setDropdown(item, open);
        });
        toggle.addEventListener('keydown', event => {
            if (event.key !== 'ArrowDown') return;
            event.preventDefault();
            closeDropdowns(item);
            setDropdown(item, true);
            menu.querySelector('a').focus({preventScroll: true});
        });
        item.addEventListener('keydown', event => {
            if (item.classList.contains('is-open')) event.stopPropagation();
            if (event.key !== 'Escape' || !item.classList.contains('is-open')) return;
            event.preventDefault();
            setDropdown(item, false);
            toggle.focus({preventScroll: true});
        });
        item.addEventListener('focusout', event => {
            if (!item.contains(event.relatedTarget)) setDropdown(item, false);
        });
    });
    document.addEventListener('click', event => {
        if (!dropdowns.some(item => item.contains(event.target))) closeDropdowns();
    });
    window.addEventListener('resize', () => closeDropdowns());

    // Match actual destinations, not textual labels or query strings.
    const path = window.location.pathname;
    document.querySelectorAll('.site-header a[href]').forEach(link => {
        const url = new URL(link.href, window.location.href);
        if (url.origin === window.location.origin && url.pathname === path && !url.hash) {
            link.setAttribute('aria-current', 'page');
        }
    });

    document.querySelectorAll('.password-toggle[data-target]').forEach(button => {
        button.addEventListener('click', () => {
            const input = document.getElementById(button.dataset.target);
            if (!input) return;
            const show = input.type === 'password';
            input.type = show ? 'text' : 'password';
            button.setAttribute('aria-pressed', String(show));
            button.setAttribute('aria-label', (show ? 'Ascunde parola: ' : 'Arată parola: ') + button.dataset.fieldLabel);
            const icon = button.querySelector('i');
            if (icon) icon.className = show ? 'fa fa-eye' : 'fa fa-eye-slash';
        });
    });

    const forms = [...document.querySelectorAll('form[data-ui-form]')];
    function validationMessage(control) {
        const validity = control.validity;
        if (validity.valueMissing) return 'Completează acest câmp.';
        if (validity.typeMismatch && control.type === 'email') return 'Introdu o adresă de email validă.';
        if (validity.tooShort) return 'Folosește cel puțin ' + control.minLength + ' caractere.';
        if (validity.tooLong) return 'Folosește cel mult ' + control.maxLength + ' caractere.';
        if (validity.rangeUnderflow) return 'Valoarea minimă este ' + control.min + '.';
        if (validity.rangeOverflow) return 'Valoarea maximă este ' + control.max + '.';
        if (validity.patternMismatch) return 'Respectă formatul cerut.';
        return 'Verifică valoarea introdusă.';
    }
    forms.forEach(form => {
        form.querySelectorAll('.form-field').forEach(field => {
            const control = field.querySelector('input, select, textarea');
            if (!control) return;
            const clientError = field.querySelector('.form-field__client-error');
            const descriptions = new Set((control.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean));
            field.querySelectorAll('.form-field__help, .form-field__errors, .form-field__client-error').forEach(el => descriptions.add(el.id));
            control.setAttribute('aria-describedby', [...descriptions].join(' '));
            if (field.classList.contains('has-error')) control.setAttribute('aria-invalid', 'true');
            function validate() {
                const invalid = control.willValidate && !control.validity.valid;
                control.setAttribute('aria-invalid', String(invalid || field.classList.contains('has-error')));
                if (clientError) {
                    clientError.textContent = invalid ? validationMessage(control) : '';
                    clientError.hidden = !invalid;
                }
            }
            control.addEventListener('blur', validate);
            control.addEventListener('invalid', validate);
            control.addEventListener('input', () => {
                if (control.getAttribute('aria-invalid') === 'true') validate();
            });
        });
        form.addEventListener('submit', event => {
            if (event.defaultPrevented) return;
            if (form.getAttribute('aria-busy') === 'true') {
                event.preventDefault();
                return;
            }
            form.setAttribute('aria-busy', 'true');
            // Disabled submit buttons are omitted from POST data. Preserve an
            // explicit action (e.g. "new equation") before disabling its button.
            if (event.submitter?.name) {
                const action = document.createElement('input');
                action.type = 'hidden';
                action.name = event.submitter.name;
                action.value = event.submitter.value;
                action.dataset.uiSubmitter = 'true';
                form.append(action);
            }
            form.querySelectorAll('button[type="submit"]').forEach(button => {
                if (button.disabled) return;
                button.disabled = true;
                button.classList.add('is-loading');
            });
            const status = document.getElementById(form.dataset.statusId);
            if (status) status.textContent = form.dataset.busyLabel || 'Se trimite…';
        });
    });
    window.addEventListener('pageshow', () => {
        updateHeader();
        // Back/Forward cache can restore the disabled DOM of a submitted form.
        forms.forEach(form => {
            if (form.getAttribute('aria-busy') !== 'true') return;
            form.removeAttribute('aria-busy');
            form.querySelectorAll('[data-ui-submitter]').forEach(input => input.remove());
            form.querySelectorAll('button.is-loading').forEach(button => {
                button.disabled = false;
                button.classList.remove('is-loading');
            });
            const status = document.getElementById(form.dataset.statusId);
            if (status) status.textContent = '';
        });
    });

    document.querySelectorAll('[data-dismissible] .message-dismiss').forEach(button => {
        button.addEventListener('click', () => {
            const message = button.closest('[data-dismissible]');
            const list = message.parentElement;
            message.remove();
            const next = list.querySelector('.message-dismiss');
            if (next) next.focus();
            else {
                list.remove();
                document.querySelector('#main-content')?.focus({preventScroll: true});
            }
        });
    });
})();
