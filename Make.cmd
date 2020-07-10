py -m venv env
call .\env\Scripts\activate
pip install -r requirements.txt
python ChannelConverter.py -r Channels -l "d:\Source\SvnDocuments\Settings\ChannelLists\Enigma2\lamedb" -o d:\Temp\DVBViewer.ini -s
call .\env\Scripts\deactivate
pause