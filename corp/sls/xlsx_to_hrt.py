import pandas as pd
import re

excel_data = pd.read_excel('Spara talet metadata - transkriptioner export.xlsx')
data = pd.DataFrame(excel_data, columns=['Signum', 'Objekt-titel', 'Filnamn','Rubrik','Titel','Orginaltext','Normaliserad text','Ordförklaringar'])
dictionary = data.to_dict(orient='record')
with open("out.hrt","w") as ouf:
	for i in dictionary:
		word_explanations = str(i['Ordförklaringar']).split("\n")
		signum = re.sub('"','&quot;',str(i['Signum']))
		signum = re.sub('"','&quot;',str(i['Signum']))		
		objekt = re.sub('"','&quot;',str(i['Objekt-titel']))
		filnamn = re.sub('"','&quot;',str(i['Filnamn']))
		rubrik = re.sub('"','&quot;',str(i['Rubrik']))
		rubrik = re.sub('\n','',rubrik)
		titel = re.sub('"','&quot;',str(i['Titel']))
		ouf.write('<text signum="'+signum+'" object="'+objekt+'" filename="'+filnamn+'" headline="'+rubrik+'" title="'+titel+'">')
		ouf.write("\n")
		if str(i['Normaliserad text']) == 'nan':
			text = str(i['Orginaltext'])			
		else:
			text = str(i['Normaliserad text'])
		text = text.split("\n")
		text = list(filter(None,text))
		for num,line in enumerate(text):
			if line.startswith('['):
				continue
			else: 
				speaker = re.match('[A-Z?-]+:',line)
				explanation = re.findall('\[\d+\]',line)
				ouf.write('<paragraph')
				if len(explanation) > 0:
					explained = []
					ouf.write(' explanation="')
					for item in explanation:
						for full_explanation in word_explanations:
							if full_explanation.startswith(item) and full_explanation not in explained:
								full_explanation = re.sub('"','&quot;',full_explanation)
								explained.append(full_explanation)
								ouf.write(full_explanation.strip())
					ouf.write('"')
				if speaker:
					speaker = re.sub(':','',speaker.group(0))
					ouf.write(' speaker="'+speaker+'"')
					if speaker == '?':
						speaker = '\\?'
					if speaker == '??':
						speaker = '\\?\\?'
					line = re.sub(speaker+': ','',line)
				try:
					if text[num+1].startswith('['):
						ouf.write(' after="'+text[num+1]+'"')
				except IndexError:
					pass
				if str(i['Normaliserad text']) != 'nan':
					original = str(i['Orginaltext']).split("\n")
					original = list(filter(None, original))
					if speaker and len(original) == len(text) and speaker in original[num]:
						original = re.sub(speaker+': ','',original[num])
						original = original.strip()
						ouf.write(' original="'+original+'"')
					elif speaker not in original:
						ouf.write(' original="not match"')
					else:
						pass
				ouf.write(">\n")
				line = re.sub('<', '&lt;', line)
				line = re.sub('>', '&gt;', line)
				line = re.sub('&', '&amp;', line)
				line = re.sub('"','&quot;', line)
				ouf.write(line+"\n")
				ouf.write('</paragraph>\n')
		ouf.write("</text>")
		ouf.write("\n")
