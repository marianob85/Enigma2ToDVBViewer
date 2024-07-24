$envDir="venv"

if( Test-Path -Path $envDir ){
	Remove-Item -Path $envDir -Recurse
}

python -m venv $envDir --system-site-packages
$activate = (Join-Path $envDir Scripts\activate)
& ".\$activate"
python -m pip install --upgrade pip
python -m pip install -I -r requirements.txt