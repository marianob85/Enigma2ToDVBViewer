py -m venv env
rem call venv\Scripts\activate.bat
.\env\Scripts\activate
pip install -r requirements.txt
python ChannelConverter.py -r Channels -l "d:\Source\SvnDocuments\Settings\ChannelLists\Enigma2\lamedb" -o d:\Temp\DVBViewer.ini -s
pause