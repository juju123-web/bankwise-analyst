from bankwise.agent import provider_error

def test_quota_classification_hides_body():
    class QuotaError(Exception):
        code = 'insufficient_quota'
        status_code = 429
    diagnostic, message = provider_error(QuotaError('secret-key-must-not-appear'))
    assert diagnostic['code']=='insufficient_quota'
    assert diagnostic['http_status']==429
    assert 'secret-key' not in str((diagnostic,message))

def test_unknown_code_is_not_echoed():
    error = RuntimeError('secret')
    error.code = 'secret'
    assert 'secret' not in str(provider_error(error))


def test_http_401_has_actionable_message_without_body():
    class AuthenticationFailure(Exception):
        status_code = 401
    diagnostic, message = provider_error(AuthenticationFailure('secret-key-do-not-print'))
    assert diagnostic['http_status'] == 401
    assert 'HTTP 401' in message and 'OPENAI_API_KEY' in message
    assert 'secret-key-do-not-print' not in str((diagnostic, message))
