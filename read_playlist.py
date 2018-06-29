import export_playlist
from cacher import dump_data, load_last_acquired_user


user = load_last_acquired_user()
exporter = export_playlist.playlistExporter(user)
print('\n'.join([str(i+1) + ' ' + p for i, p in enumerate(exporter.get_praylists())]))
print()
playlist_number_to_export = 0
while playlist_number_to_export == 0:
    playlist_number_to_export = int(raw_input("Enter the number of playlist to export: "))
print exporter.get_export_file(playlist_number_to_export)
