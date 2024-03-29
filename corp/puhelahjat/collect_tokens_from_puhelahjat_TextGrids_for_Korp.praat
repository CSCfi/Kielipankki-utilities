# Puhelahjat: VRT-versio Korpia varten
#
# Kerätään Puhelahjat-aineiston TextGrid-tiedostoista kaikki kohdistetut saneet ja näiden 
# alku- ja loppuajat Korpiin vientiä varten.
#
# Luetaan annetusta hakemistosta löytyvät TextGrid-tiedostot yksi kerrallaan 
# ja kerätään annotaatiokerroksesta numero 1
# (melkein) VRT-muotoiseen tiedostoon yksittäiset saneet (sane/rivi) sekä 
# sarkainmerkeillä eroteltuina jokaisen alku- ja loppuaika sekä kesto sekunteina.
#
# VRT-tiedoston alkuun lisätään <text>-elementti, johon sisältyy 
# - tiedoston nimi (ilman tiedostopäätettä)
# - clientId (tiedostonimen alkuosa ensimmäiseen _-merkkiin saakka); vastaa oletettavasti yleensä yksittäistä "puhujaa"
# - kyseisen TextGrid-tiedoston (=vastaavan äänitiedoston) kesto käyttäjäystävällisessä muodossa h:min:s.xxx
# sekä tiedoston loppuun elementin lopetustagi.
#
# (Tässä vaiheessa tällä aineistolla ei käytetä vielä lainkaan <p>- tai <s>-tageja. Tehdään ne vasta sitten, kun 
# verrataan kohdistettuja saneita tekstimuotoisiin litteraatteihin, joista näkyy, minkä saneiden välissä kunkin puhunnoksen 
# on suunnilleen ajateltu katkeavan.)
#
# Skripti jättää automaattisesti tiedoston ensimmäisen ja viimeisen intervallin pois VRT:stä, mikäli nämä ovat tyhjiä.
# Muilta osin myös tauot ovat mukana "tyhjinä" saneina.
# (Sanaa edeltävä tai seuraava tauko (+ tauon kesto) halutaan mahdollisesti kirjata Korp-versioon sanan ominaisuuksina?)
#
# Lisäksi kerätään erilliseen sarkaineroteltuun tiedostoon "file_locations.tsv" tieto kunkin tiedoston sijainnista 
# aineiston latausversiossa 1. Tarkoitus on helpottaa tiedostojen paikantamista eri latauspaketeissa.
# Sarakkeiden nimet ovat clientId, recordingId, fileLocation.
#
# Skriptin voi ajaa komentoriviltä, kun siirtyy puhelahjat-päähakemistoon, johon tämä skripti on tallennettu, 
# ja antaa komennon "praat collect_tokens_from_puhelahjat_TextGrids_for_Korp.praat".
# Tämä edellyttää toki, että Praat on asennettuna ja polulla.
# (Nopeampiakin tapoja tämän tiedon keräämiseen on olemassa, mutta tämä skripti oli tänään helposti saatavilla.)
#
# 13.12.2022 Mietta Lennes
#
#

grid_dir_1$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_01/alignments/manual_2022-04-22/"
grid_dir_2$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_02/alignments/manual_2022-04-22/"
grid_dir_3$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_03/alignments/manual_2022-04-22/"
grid_dir_4$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_04/alignments/manual_2022-04-22/"
grid_dir_5$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_05/alignments/manual_2022-04-22/"
grid_dir_6$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_06/alignments/manual_2022-04-22/"
grid_dir_7$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_07/alignments/manual_2022-04-22/"
grid_dir_8$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_08/alignments/manual_2022-04-22/"
grid_dir_9$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_09/alignments/manual_2022-04-22/"
grid_dir_10$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_10/alignments/manual_2022-04-22/"
grid_dir_11$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_11/alignments/manual_2022-04-22/"
grid_dir_12$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_12/alignments/manual_2022-04-22/"
grid_dir_13$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_13/alignments/manual_2022-04-22/"
grid_dir_14$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_14/alignments/manual_2022-04-22/"
grid_dir_15$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_15/alignments/manual_2022-04-22/"
grid_dir_16$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_16/alignments/manual_2022-04-22/"
grid_dir_17$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_17/alignments/manual_2022-04-22/"
grid_dir_18$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_18/alignments/manual_2022-04-22/"
grid_dir_19$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_19/alignments/manual_2022-04-22/"
grid_dir_20$ = "/Users/lennes/corpora/puhelahjat/v1/2020_part_20/alignments/manual_2022-04-22/"
grid_dir_21$ = "/Users/lennes/corpora/puhelahjat/v1/2021_part_01/alignments/manual_2022-04-22/"

korp_vrt_dir$ = "Korp/"
file_info_table$ = "file_locations.tsv"
deleteFile: file_info_table$
fileappend 'file_info_table$' clientId	recordingId	fileLocation'newline$'


for grid from 1 to 21

appendInfoLine: ""
appendInfoLine: "Export the aligned Puhelahjat data to preliminary VRT for Korp"

textgrid_dir$ = grid_dir_'grid'$
#textgrid_dir$ = chooseFolder$: "Select the TextGrid folder"

#----------

appendInfoLine: "Analyzing: " + textgrid_dir$

# Figure out the original locations of the corresponding TextGrid and audio under the "puhelahjat" directory tree:
original_textgrid_folder$ = right$ (textgrid_dir$, length(textgrid_dir$)-index(textgrid_dir$,"puhelahjat")+1)
original_subfolder$ = left$ (original_textgrid_folder$, index(original_textgrid_folder$,"alignments")-1)
original_audio_folder$ = left$ (original_textgrid_folder$, index(original_textgrid_folder$,"alignments")-1) + "audio/"

# See how many TextGrid files there are:
Create Strings as file list: "files", "'textgrid_dir$'/*.TextGrid"
numberOfFiles = Get number of strings
appendInfoLine: "Files: 'numberOfFiles'"

	# Uncomment the following line, if you want to pause the script 
	# before starting to process the next list of TextGrids:
	#pause

for file to numberOfFiles

	select Strings files
	string$ = Get string... file
	file$ = textgrid_dir$ + "/" + string$
	Read from file: file$
	gridname$ = selected$ ("TextGrid", 1)
	total_duration = Get total duration
	call ConvertSecondsToHrMinSec total_duration total_duration$

	clientId$ = left$ (gridname$, index(gridname$, "_") - 1)

	# Save the VRT header:
	table_file$ = "'korp_vrt_dir$''gridname$'.vrt"
	deleteFile: table_file$
	line$ = "<text name=""'gridname$'"" clientId=""'clientId$'"" recordingDuration=""'total_duration$'"">"
	fileappend 'table_file$' 'line$''newline$'

	# Process only one annotation tier in each TextGrid file (all other tiers will be ignored, if any)
	root_tier = 1
			
			# Collect the individual words to the tabulated text (VRT) file:
			numberOfRootIntervals = Get number of intervals... root_tier
			for root_interval to numberOfRootIntervals
				root_interval$ = Get label of interval... root_tier root_interval
				# Exclude pause at the beginning of the file and pause at the end, but otherwise include pauses (empty intervals):
				if root_interval$ <> "" or (root_interval <> 1 and root_interval <> numberOfRootIntervals)					
					beg = Get starting point: root_tier, root_interval
					end = Get end point: root_tier, root_interval
					dur = end - beg
					# Save the information about the word interval:
					line$ = "'root_interval$'	'beg'	'end'	'dur:2'"
					fileappend 'table_file$' 'line$''newline$'
				endif
			endfor

	# Finally, close the VRT document:
	line$ = "</text>"
	fileappend 'table_file$' 'line$''newline$'

	# Remove the TextGrid
	Remove

	file_metadata$ = "'clientId$'	'gridname$'	'original_subfolder$'"
	fileappend 'file_info_table$' 'file_metadata$''newline$'
	
	# Uncomment the following line, if you want to pause the script between consecutive TextGrids (for testing):
	#pause

endfor

appendInfoLine: "Finished!"

select Strings files
Remove

endfor

#-------------
procedure ConvertSecondsToHrMinSec variable1 variable2$

	tmp$ = ""

	hrs = floor (variable1 / 60 / 60)
	hrs$ = "'hrs'"
	if length(hrs$) = 1
		hrs$ = "0'hrs$'"
	endif
	variable1 = variable1 - (360 * hrs)
	mins = floor (variable1 / 60)
	mins$ = "'mins'"
	if length(mins$) = 1
		mins$ = "0'mins$'"
	endif
	variable1 = variable1 - (60 * mins)
	tmp$ = "'hrs$':'mins$':'variable1:2'"

	'variable2$' = tmp$

endproc
