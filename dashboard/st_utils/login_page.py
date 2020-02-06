import os
import streamlit as st

import dashboard.st_utils.session_state as SessionState


class LoginPage():
    def __init__(self, session_image_path=os.environ.get('CHALLENGE_LOGO')):
        # self.login_image_path = login_image_path
        self.session_image_path = session_image_path
        self.session = SessionState.get(user_name='', password='')

    def __enter__(self):
        if self.valid_credentials():
            return self._enter_return()

        # st.image(self.login_image_path, use_column_width=True)

        self.session.user_name = st.text_input(
            'Login',
            value=self.session.user_name,
            key=None,
            type='default',
        ).title()

        self.session.password = st.text_input(
            'Password',
            value=self.session.password,
            key=None,
            type='password',
        )

        if st.button('Login'):
            if self.valid_credentials():
                return self._enter_return()
            else:
                st.error('Unvalid credentials.')

    def __exit__(self, type, value, traceback):
        pass

    def _enter_return(self):
        if self.valid_credentials():
            st.sidebar.image(self.session_image_path, use_column_width=True)
            st.sidebar.markdown(f'**Session : {self.session.user_name}** (Refresh page to disconnect.) \n ---')
        return self.session

    def valid_credentials(self):
        if os.environ.get('CHALLENGE_NO_LOGIN_REQUIRED'):
            return True
        return (self.session.user_name.lower() == os.environ.get('CHALLENGE_LOGIN').lower()
                and self.session.password.lower() == os.environ.get('CHALLENGE_LOGIN').lower())
