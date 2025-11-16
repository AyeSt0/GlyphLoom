from glyphloom_core.qa.placeholder_check import check_placeholder_consistency


def test_consistency_ok_no_issue() -> None:
    source = "Hello {user}, id={{id}} <br> %s"
    target = "你好 {user}，编号 {{id}} <br> %s"
    issues = check_placeholder_consistency(source, target, row=1)
    assert issues == []


def test_missing_placeholder() -> None:
    source = "Hello {user}, id={{id}}, ctx <c>"
    target = "你好 {user}, ctx"
    issues = check_placeholder_consistency(source, target, row=2)
    assert len(issues) == 2
    placeholders = {i.placeholder for i in issues}
    assert placeholders == {"{{id}}", "<c>"}
    assert all("缺少占位符" in i.message for i in issues)


def test_extra_placeholder() -> None:
    source = "Hello {user}"
    target = "你好 {user} 和 {{extra}} %s"
    issues = check_placeholder_consistency(source, target, row=3)
    placeholders = {i.placeholder for i in issues}
    assert placeholders == {"{{extra}}", "%s"}
    assert all("多出占位符" in i.message for i in issues)


def test_whitelist_ignored() -> None:
    source = "文本 {keep} 和 {optional}"
    target = "文本 {keep}"
    issues = check_placeholder_consistency(
        source, target, row=4, whitelist={"{optional}"}
    )
    assert issues == []
