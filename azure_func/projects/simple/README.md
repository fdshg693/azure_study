Azure Functionのローカル起動
```powershell
cd C:\CodeStudy\azure_study\azure_func\projects\simple
func start
```

テストの実行
```powershell
cd C:\CodeStudy\azure_study\azure_func
$env:AZURE_FUNCTION_URL="http://localhost:7071"
uv run pytest projects\simple\tests
```