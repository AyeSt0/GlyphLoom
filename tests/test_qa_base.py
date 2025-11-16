from glyphloom_core.qa.base import Issue, QAResult, run


def test_empty_input_returns_empty() -> None:
    """空输入应返回空问题列表。"""

    issues = run([])
    assert issues == []


def test_no_rules_returns_empty() -> None:
    """无规则实现时也应安全返回空列表，不抛异常。"""

    sample = ["{user}", "%s", "<tag>"]
    issues = run(sample)
    assert issues == []


def test_issue_dataclass_fields() -> None:
    """Issue/QAResult 模型按预期存储字段。"""

    issue = Issue(row=1, placeholder="{user}", message="missing translation")
    result = QAResult(issues=[issue])
    assert result.issues[0].row == 1
    assert result.issues[0].placeholder == "{user}"
    assert result.issues[0].message == "missing translation"
