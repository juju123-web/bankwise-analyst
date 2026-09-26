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
