import io

import pytest
import requests

import cleverbot


@pytest.fixture
def cb(request, monkeypatch):
    cb = cleverbot.Cleverbot('API_KEY', cs='76nxdxIJ02AAA', timeout=60,
                             tweak1=25, tweak2=50, tweak3=75)
    if hasattr(request, 'param'):
        def mock_get(url, params, timeout):

            class MockResponse(object):
                def __init__(self):
                    if request.param.get('timeout'):
                        raise requests.Timeout
                    if request.param.get('params'):
                        assert params == request.param['params']
                    self.status_code = request.param.get('status', 200)

                def json(self):
                    return request.param.get('json', {
                        'output': 'test', 'cs': 'cs', 'test': 'test'
                    })

            return MockResponse()
        monkeypatch.setattr(cb.session, 'get', mock_get)
    return cb


@pytest.fixture
def cb_nameless():
    cb = cleverbot.Cleverbot('API_KEY', cs='76nxdxIJ02AAA', timeout=60,
                             tweak1=25, tweak2=50, tweak3=75)
    for i, s in enumerate(map(str, range(200))):
        cb.conversation(key=s, cs=s, timeout=i)
    return cb


@pytest.fixture
def cb_named():
    cb = cleverbot.Cleverbot('API_KEY', cs='76nxdxIJ02AAA', timeout=60,
                             tweak1=25, tweak2=50, tweak3=75)
    for i, s in enumerate(map(str, range(200))):
        cb.conversation(s, key=s, cs=s, timeout=i)
    return cb


class TestCleverbot:

    def test_init(self):
        cb = cleverbot.Cleverbot('API_KEY', cs='76nxdxIJ02AAA', timeout=60,
                                 tweak1=25, tweak2=50, tweak3=75)
        assert cb.key == 'API_KEY'
        assert cb.cs == '76nxdxIJ02AAA'
        assert cb.timeout == 60
        assert cb.tweak1 == 25
        assert cb.tweak2 == 50
        assert cb.tweak3 == 75

    def test_cs(self):
        cb = cleverbot.Cleverbot(None, cs='76nxdxIJ02AAA')
        assert cb.cs == cb.data['cs']
        cb.cs = 'test'
        assert cb.cs == 'test'

    def test_getattr(self, cb):
        cb.data = {'test': 'value'}
        assert cb.test == 'value'

    @pytest.mark.parametrize(
        'cb', [
            {'params': {
                'input': 'test', 'key': 'key', 'cs': 'cs',
                'wrapper': 'cleverbot.py', 'cb_settings_tweak1': 5,
                'cb_settings_tweak2': 10, 'cb_settings_tweak3': 15,
                'test': 'test'
            }}
        ], indirect=True
    )
    def test_say_params(self, cb):
        cb.say('test', key='key', cs='cs', tweak1=5, tweak2=10, tweak3=15,
               test='test')

    @pytest.mark.parametrize(
        'cb', [
            {'params': {
                'key': 'API_KEY', 'cs': '76nxdxIJ02AAA',
                'wrapper': 'cleverbot.py', 'cb_settings_tweak1': 25,
                'cb_settings_tweak2': 50, 'cb_settings_tweak3': 75
            }}
        ], indirect=True
    )
    def test_say_params_empty(self, cb):
        cb.say()

    @pytest.mark.parametrize(
        'cb', [
            {'status': 200, 'json': {
                'output': 'test', 'cs': 'cs', 'test': 'test'
            }}
        ], indirect=True
    )
    def test_say(self, cb):
        assert cb.say() == 'test'
        assert cb.cs == 'cs'
        assert cb.test == 'test'

    @pytest.mark.parametrize(
        'cb', [
            {'status': 401, 'json': {'status': 401, 'error': 'text'}}
        ], indirect=True
    )
    def test_say_apierror(self, cb):
        with pytest.raises(cleverbot.APIError, message='text'):
            try:
                cb.say()
            except cleverbot.APIError as e:
                assert e.status == 401
                raise

    @pytest.mark.parametrize(
        'cb', [{'status': 401, 'json': {}}], indirect=True)
    def test_say_apierror_empty(self, cb):
        with pytest.raises(cleverbot.APIError):
            cb.say()

    @pytest.mark.parametrize('cb', [{'timeout': True}], indirect=True)
    def test_say_timeout(self, cb):
        with pytest.raises(cleverbot.Timeout):
            try:
                cb.say()
            except cleverbot.Timeout as e:
                assert e.timeout == cb.timeout
                raise

    def test_conversation_empty(self, cb):
        convo = cb.conversation()
        assert convo.key == cb.key
        assert convo.cs is None
        assert convo.timeout == cb.timeout
        assert convo.tweak1 == cb.tweak1
        assert convo.tweak2 == cb.tweak2
        assert convo.tweak3 == cb.tweak3

    def test_conversation_nameless(self, cb):
        convo = cb.conversation(
            key='key', cs='cs', timeout=10, tweak1=5, tweak2=10, tweak3=15)
        assert convo.key == 'key'
        assert convo.cs == 'cs'
        assert convo.timeout == 10
        assert convo.tweak1 == 5
        assert convo.tweak2 == 10
        assert convo.tweak3 == 15

    def test_conversation_named(self, cb):
        convo = cb.conversation('name', key='key', cs='cs', timeout=10,
                                tweak1=5, tweak2=10, tweak3=15)
        assert convo.key == 'key'
        assert convo.cs == 'cs'
        assert convo.timeout == 10
        assert convo.tweak1 == 5
        assert convo.tweak2 == 10
        assert convo.tweak3 == 15

    def test_conversations_nameless(self, cb):
        for i, s in enumerate(map(str, range(200))):
            cb.conversation(
                key=s, cs=s*2, timeout=i, tweak1=i, tweak2=i+5, tweak3=i+10)
        convos = cb.conversations
        for convo, (i, s) in zip(convos, enumerate(map(str, range(200)))):
            items = zip(('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3'),
                        (s, s*2, i, i, i+5, i+10))
            for item, value in items:
                assert getattr(convo, item) == value

    def test_conversations_named(self, cb):
        convos = {}
        for i, s in enumerate(map(str, range(200))):
            convos[s] = cb.conversation(
                s, key=s, cs=s*2, timeout=i, tweak1=i, tweak2=i+5, tweak3=i+10)
        for name, convo1 in cb.conversations.items():
            convo2 = convos[name]
            for item in ('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3'):
                assert getattr(convo1, item) == getattr(convo2, item)

    def test_reset_nameless(self, cb_nameless):
        cb_nameless.reset()
        assert not cb_nameless.data
        for convo in cb_nameless.conversations:
            assert not convo.data

    def test_reset_named(self, cb_named):
        cb_named.reset()
        assert not cb_named.data
        for convo in cb_named.conversations.values():
            assert not convo.data


class TestConversation:

    @pytest.fixture
    def convo(self, cb, request, monkeypatch):
        convo = cb.conversation(key='API_KEY', cs='76nxdxIJ02AAA', timeout=60,
                                tweak1=25, tweak2=50, tweak3=75)
        if hasattr(request, 'param'):
            def mock_get(url, params, timeout):

                class MockResponse(object):
                    def __init__(self):
                        if request.param.get('timeout'):
                            raise requests.Timeout
                        if request.param.get('params'):
                            assert params == request.param['params']
                        self.status_code = request.param.get('status', 200)

                    def json(self):
                        return request.param.get('json', {
                            'output': 'test', 'cs': 'cs', 'test': 'test'
                        })

                return MockResponse()
            monkeypatch.setattr(convo.session, 'get', mock_get)
        return convo

    def test_cs(self, cb):
        convo = cb.conversation(cs='76nxdxIJ02AAA')
        assert convo.cs == cb.cs
        convo.cs = 'test'
        assert convo.cs == 'test'

    def test_getattr(self, convo):
        convo.data = {'test': 'value'}
        assert convo.test == 'value'

    @pytest.mark.parametrize(
        'convo', [
            {'params': {
                'input': 'test', 'key': 'key', 'cs': 'cs',
                'wrapper': 'cleverbot.py', 'cb_settings_tweak1': 5,
                'cb_settings_tweak2': 10, 'cb_settings_tweak3': 15,
                'test': 'test'
            }}
        ], indirect=True
    )
    def test_say_params(self, convo):
        convo.say('test', key='key', cs='cs', tweak1=5, tweak2=10, tweak3=15,
                  test='test')

    @pytest.mark.parametrize(
        'convo', [
            {'params': {
                'key': 'API_KEY', 'cs': '76nxdxIJ02AAA',
                'wrapper': 'cleverbot.py', 'cb_settings_tweak1': 25,
                'cb_settings_tweak2': 50, 'cb_settings_tweak3': 75
            }}
        ], indirect=True
    )
    def test_say_params_empty(self, convo):
        convo.say()

    @pytest.mark.parametrize(
        'convo', [
            {'status': 200, 'json': {
                'output': 'test', 'cs': 'cs', 'test': 'test'
            }}
        ], indirect=True
    )
    def test_say(self, convo):
        assert convo.say() == 'test'
        assert convo.cs == 'cs'
        assert convo.test == 'test'

    @pytest.mark.parametrize(
        'convo', [
            {'status': 401, 'json': {'status': 401, 'error': 'text'}}
        ], indirect=True
    )
    def test_say_apierror(self, convo):
        with pytest.raises(cleverbot.APIError, message='text'):
            try:
                convo.say()
            except cleverbot.APIError as e:
                assert e.status == 401
                raise

    @pytest.mark.parametrize(
        'convo', [{'status': 401, 'json': {}}], indirect=True)
    def test_say_apierror_empty(self, convo):
        with pytest.raises(cleverbot.APIError):
            convo.say()

    @pytest.mark.parametrize('convo', [{'timeout': True}], indirect=True)
    def test_say_timeout(self, convo):
        with pytest.raises(cleverbot.Timeout):
            try:
                convo.say()
            except cleverbot.Timeout as e:
                assert e.timeout == convo.timeout
                raise

    def test_reset(self, convo):
        convo.reset()
        assert not convo.data


class TestIO:

    def test_cleverbot_save_nameless(self, cb_nameless):
        with io.BytesIO() as f:
            cb_nameless.save(f)
            assert f.getvalue()

    def test_cleverbot_save_named(self, cb_named):
        with io.BytesIO() as f:
            cb_named.save(f)
            assert f.getvalue()

    def test_cleverbot_load_nameless(self, cb, cb_nameless):
        with io.BytesIO() as f:
            cb_nameless.save(f)
            with io.BytesIO(f.getvalue()) as f:
                cb.load(f)
        for convo1, convo2 in zip(cb.conversations, cb_nameless.conversations):
            for item in ('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3'):
                assert getattr(convo1, item) == getattr(convo2, item)

    def test_cleverbot_load_named(self, cb, cb_named):
        convos = cb_named.conversations
        with io.BytesIO() as f:
            cb_named.save(f)
            with io.BytesIO(f.getvalue()) as f:
                cb.load(f)
        for name, convo1 in cb.conversations.items():
            convo2 = convos[name]
            for item in ('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3'):
                assert getattr(convo1, item) == getattr(convo2, item)

    def test_load_nameless(self, cb_nameless):
        with io.BytesIO() as f:
            cb_nameless.save(f)
            with io.BytesIO(f.getvalue()) as f:
                cb = cleverbot.load(f)
        for item in ('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3'):
            assert getattr(cb, item) == getattr(cb_nameless, item)
        for convo1, convo2 in zip(cb.conversations, cb_nameless.conversations):
            for item in ('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3'):
                assert getattr(convo1, item) == getattr(convo2, item)

    def test_load_named(self, cb_named):
        convos = cb_named.conversations
        with io.BytesIO() as f:
            cb_named.save(f)
            with io.BytesIO(f.getvalue()) as f:
                cb = cleverbot.load(f)
        for item in ('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3'):
            assert getattr(cb, item) == getattr(cb_named, item)
        for name, convo1 in cb.conversations.items():
            convo2 = convos[name]
            for item in ('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3'):
                assert getattr(convo1, item) == getattr(convo2, item)
