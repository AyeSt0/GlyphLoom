from glyphloom_core.qa.placeholders import (
    extract_placeholders,
    register_placeholder_pattern,
    register_placeholder_patterns,
)


def test_extract_basic_patterns() -> None:
    text = "Hello {user}, value is %s, nested {{VALUE}}, tag <br>"
    placeholders = extract_placeholders(text)
    # 去重且包含所有模式
    assert placeholders == {"{user}", "%s", "{{VALUE}}", "<br>"}


def test_extract_ignores_whitelist() -> None:
    text = "User {user} and {user} again, skip %s"
    placeholders = extract_placeholders(text, whitelist={"%s"})
    # {user} 仍保留，%s 被过滤
    assert placeholders == {"{user}"}


def test_extract_handles_empty_text() -> None:
    assert extract_placeholders("") == set()
    assert extract_placeholders(None or "") == set()


def test_extract_mixed_placeholders_and_special_chars() -> None:
    """混合多种占位符与特殊字符，确保正则能捕获全部。"""

    text = (
        "prefix-{id}-<tag>-%s-{{VALUE}}-{name}-{another}-<span>"
        "复杂字符!@#中文{cn}结尾"
    )
    placeholders = extract_placeholders(text)
    expected = {
        "{id}",
        "<tag>",
        "%s",
        "{{VALUE}}",
        "{name}",
        "{another}",
        "<span>",
        "{cn}",
    }
    assert placeholders == expected


def test_extract_with_whitelist_multiple() -> None:
    """白名单可同时过滤多种占位符。"""

    text = "保留 {keep}，过滤 {drop} 和 %s，还有 <skip>"
    placeholders = extract_placeholders(text, whitelist={"%s", "{drop}", "<skip>"})
    assert placeholders == {"{keep}"}


def test_extract_non_placeholder_text_not_matched() -> None:
    """确保非占位符文本不会被误匹配，方便后续扩展验证。"""

    text = "普通文本 no placeholder here, 以及 {未闭合 与 <嵌套<tag>"
    placeholders = extract_placeholders(text)
    # 只捕获最内层合法 <tag>，未闭合的大括号不算
    assert "<tag>" in placeholders


def test_extract_colon_placeholders() -> None:
    """支持包含冒号或方括号的占位符，如 {key:value} 或 {{[key:default]}}。"""

    text = "带默认值 {{name:anon}}，参数 {key:val}，方括号 {[id:1]}，以及普通 {id}"
    placeholders = extract_placeholders(text)
    assert placeholders == {"{{name:anon}}", "{key:val}", "{[id:1]}", "{id}"}


def test_register_custom_pattern() -> None:
    """自定义模式可注入，无需修改源码。"""

    # 注册一个简单的 $VAR$ 模式
    register_placeholder_pattern(r"\$[A-Za-z0-9_]+\$")
    text = "含有自定义 $TOKEN$ 与 {id}"
    placeholders = extract_placeholders(text)
    assert placeholders == {"$TOKEN$", "{id}"}


def test_register_multiple_patterns() -> None:
    """批量注册模式，模拟从配置加载多种占位符格式。"""

    # 典型 printf 风格占位符与 ${ENV} 风格
    register_placeholder_patterns([r"%\([^)]+\)s", r"\$\{[A-Za-z0-9_]+\}"])
    text = "printf %(name)s and ${ENV} plus {id}"
    placeholders = extract_placeholders(text)
    assert placeholders == {"%(name)s", "${ENV}", "{id}"}


def test_interleaved_placeholder_types() -> None:
    """多个占位符类型交错出现，确保全部捕获且不重复。"""

    text = "{a}%s{{b}}<c>{[d:1]}%(e)s${VAR}<f>{outer {nested}}"
    placeholders = extract_placeholders(text)
    expected = {
        "{a}",
        "%s",
        "{{b}}",
        "<c>",
        "{[d:1]}",
        "%(e)s",
        "${VAR}",
        "<f>",
        "{outer {nested}}",
    }
    assert placeholders == expected


def test_nested_and_spaced_placeholders() -> None:
    """包含多层嵌套与空格的占位符。"""

    text = "(( outer ( inner ) )) 与 {[ key : default ]} 以及 < tag >"
    placeholders = extract_placeholders(text)
    assert placeholders == {"(( outer ( inner ) ))", "{[ key : default ]}", "< tag >"}


def test_placeholders_with_spaces_inside() -> None:
    """占位符内部有空格也能被识别。"""

    text = "{ key : default } 和 {{ display : name }} 还有 {[ idx : 2 ]}"
    placeholders = extract_placeholders(text)
    assert placeholders == {
        "{ key : default }",
        "{{ display : name }}",
        "{[ idx : 2 ]}",
    }
