# Caminho do arquivo a ser executado
$arquivo = "C:\projetos\python\users_sapiens\app.py"

# Verifica se o arquivo existe antes de executá-lo
if (Test-Path $arquivo) {
    # Executa o arquivo Python
    & python $arquivo
} else {
    Write-Host "O arquivo $arquivo não foi encontrado."
}
