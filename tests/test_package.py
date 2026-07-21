import proompt


def test_public_api_exports():
    expected = {
        "BaseProvider",
        "Context",
        "ToolContext",
        "PromptSection",
        "BasePrompt",
        "FileDataProvider",
        "CsvDataProvider",
        "SqliteProvider",
        "TableData",
        "to_markdown_table",
    }
    assert expected <= set(proompt.__all__)
    for name in expected:
        assert hasattr(proompt, name)
