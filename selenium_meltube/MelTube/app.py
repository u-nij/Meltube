import from_melon
import to_youtube_music

type, playlist_element_list = from_melon.import_melon_playlist()
song_list = from_melon.edit_playlist_element_list(type, playlist_element_list)
title_of_file, num_of_file = from_melon.create_excel_file(song_list)

to_youtube_music.to_youtube_music(title_of_file, num_of_file)