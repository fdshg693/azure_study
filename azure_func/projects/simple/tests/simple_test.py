"""
Azure Function の統合テスト

このテストは実際のデプロイ済み Azure Function エンドポイントに対して
HTTP リクエストを送信し、動作を検証します。

環境設定:
- 環境変数 AZURE_FUNCTION_URL にベース URL を設定
- または pytest の --base-url オプションで指定

実行例:
    pytest tests/simple_test.py
    pytest tests/simple_test.py --base-url https://your-function.azurewebsites.net
"""

import os
import pytest
import requests


@pytest.fixture
def base_url(request):
    """
    Azure Function のベース URL を取得する fixture
    
    優先順位:
    1. pytest の --base-url オプション
    2. 環境変数 AZURE_FUNCTION_URL
    
    Returns:
        str: ベース URL（末尾のスラッシュなし）
    
    Raises:
        pytest.skip: URL が設定されていない場合
    """
    # pytest-base-url が提供する base_url を優先
    url = request.config.getoption("--base-url", default=None)
    
    # オプションがなければ環境変数から取得
    if not url:
        url = os.getenv("AZURE_FUNCTION_URL")
    
    # どちらも設定されていない場合はテストをスキップ
    if not url:
        pytest.skip(
            "Azure Function URL が設定されていません。\n"
            "環境変数 AZURE_FUNCTION_URL を設定するか、\n"
            "pytest --base-url オプションで URL を指定してください。"
        )
    
    # 末尾のスラッシュを削除
    return url.rstrip("/")


@pytest.fixture
def function_endpoint(base_url):
    """
    MyHttpTrigger 関数のエンドポイント URL を返す fixture
    
    Args:
        base_url: ベース URL fixture
    
    Returns:
        str: 完全なエンドポイント URL
    """
    return f"{base_url}/api/MyHttpTrigger"


def test_http_trigger_with_query_param(function_endpoint):
    """
    クエリパラメータで name を渡すテスト
    
    期待値:
    - ステータスコード: 200
    - レスポンスに "Hello, TestUser" が含まれる
    """
    # クエリパラメータで name を指定してリクエスト
    response = requests.get(function_endpoint, params={"name": "TestUser"}, timeout=30)
    
    # ステータスコードの確認
    assert response.status_code == 200, (
        f"期待されるステータスコード: 200, 実際: {response.status_code}\n"
        f"レスポンス: {response.text}"
    )
    
    # レスポンス内容の確認
    response_text = response.text
    assert "Hello, TestUser" in response_text, (
        f"レスポンスに 'Hello, TestUser' が含まれていません。\n"
        f"実際のレスポンス: {response_text}"
    )
    
    print(f"✓ クエリパラメータテスト成功: {response_text}")


def test_http_trigger_with_body_param(function_endpoint):
    """
    JSON ボディで name を渡すテスト
    
    期待値:
    - ステータスコード: 200
    - レスポンスに "Hello, BodyUser" が含まれる
    """
    # JSON ボディで name を指定してリクエスト
    response = requests.post(
        function_endpoint,
        json={"name": "BodyUser"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    # ステータスコードの確認
    assert response.status_code == 200, (
        f"期待されるステータスコード: 200, 実際: {response.status_code}\n"
        f"レスポンス: {response.text}"
    )
    
    # レスポンス内容の確認
    response_text = response.text
    assert "Hello, BodyUser" in response_text, (
        f"レスポンスに 'Hello, BodyUser' が含まれていません。\n"
        f"実際のレスポンス: {response_text}"
    )
    
    print(f"✓ JSONボディテスト成功: {response_text}")


def test_http_trigger_without_param(function_endpoint):
    """
    パラメータなしでリクエストするテスト
    
    期待値:
    - ステータスコード: 200
    - デフォルトメッセージが返される
    """
    # パラメータなしでリクエスト
    response = requests.get(function_endpoint, timeout=30)
    
    # ステータスコードの確認
    assert response.status_code == 200, (
        f"期待されるステータスコード: 200, 実際: {response.status_code}\n"
        f"レスポンス: {response.text}"
    )
    
    # レスポンス内容の確認（デフォルトメッセージ）
    response_text = response.text
    assert "Pass a name in the query string or in the request body" in response_text, (
        f"デフォルトメッセージが含まれていません。\n"
        f"実際のレスポンス: {response_text}"
    )
    
    print(f"✓ パラメータなしテスト成功: {response_text}")


def test_http_trigger_connection(function_endpoint):
    """
    エンドポイントへの接続テスト（補助的なテスト）
    
    接続エラーが発生した場合、わかりやすいエラーメッセージを表示
    """
    try:
        response = requests.get(function_endpoint, timeout=30)
        assert response.status_code in [200, 400, 404], (
            f"予期しないステータスコード: {response.status_code}"
        )
        print(f"✓ 接続テスト成功: エンドポイントに到達できました")
    except requests.exceptions.ConnectionError as e:
        pytest.fail(
            f"Azure Function エンドポイントに接続できません。\n"
            f"URL: {function_endpoint}\n"
            f"エラー: {str(e)}\n"
            f"Azure Function がデプロイされ、実行中であることを確認してください。"
        )
    except requests.exceptions.Timeout as e:
        pytest.fail(
            f"Azure Function エンドポイントへのリクエストがタイムアウトしました。\n"
            f"URL: {function_endpoint}\n"
            f"エラー: {str(e)}"
        )
