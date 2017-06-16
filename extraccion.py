from lxml import etree
from os import sys
import collections

posId = list()
nerId = list()
arreglo = []
for archivo in sys.argv[1:]:
	
	#variables
	#pos = []
	#ners = []
	id = None
	cuentaPos = {}
	primerLugarPos = {}
	ultimoLugarPos = {}
	secuenciaMasLargaPos = {}
	cuentaNer = {}
	primerLugarNer = {}
	ultimoLugarNer = {}
	secuenciaMasLargaNer = {}
	primerPos = None
	primerNer = None
	cuentaNormalizedNer = {}

	#temporal
	tmpSecuenciaMasLargaPos = {}
	tmpSecuenciaMasLargaNer = {}

	#parseado de xml	
	salida = etree.parse(archivo)
	document = salida.getroot().find("document")
	id = document.find("id").text
	tokens = []
	sentences = document.find("sentences").getchildren()
	for sentence in sentences:
		sentence = sentence.find("tokens")
		for x in sentence.getchildren():
			tokens.append(x)
	#recorrido
	for idx, token in enumerate(tokens):
		pos = token.find("POS")
		ner = pos.getnext()
		normalizedNer = ner.getnext()

		if(idx == 0):
			if(pos.text not in posId):
				posId.append(pos.text)
			if(ner.text not in nerId):
				nerId.append(ner.text)
			primerPos = posId.index(pos.text)+1
			primerNer = nerId.index(ner.text)+1
		if(pos.text in cuentaPos.keys()):	
			cuentaPos[pos.text] += 1
			ultimoLugarPos[pos.text] = idx+1
			if(tmpSecuenciaMasLargaPos[pos.text]["fin"] == idx):
				#secuenciaMasLargaPos[pos.text]["fin"] = idx+1
				tmpSecuenciaMasLargaPos[pos.text]["fin"] = idx+1
			#else:
				if((secuenciaMasLargaPos[pos.text]["fin"]-secuenciaMasLargaPos[pos.text]["inicio"])<(tmpSecuenciaMasLargaPos[pos.text]["fin"]-tmpSecuenciaMasLargaPos[pos.text]["inicio"])):
					secuenciaMasLargaPos[pos.text]["fin"] = tmpSecuenciaMasLargaPos[pos.text]["fin"]
					secuenciaMasLargaPos[pos.text]["inicio"] = tmpSecuenciaMasLargaPos[pos.text]["inicio"]
					
		else:
			cuentaPos[pos.text] = 1
			primerLugarPos[pos.text] = idx+1
			ultimoLugarPos[pos.text] = idx+1#La primera aunque sea unica, tambien es la ultima
			secuenciaMasLargaPos[pos.text] = {"inicio":idx+1,"fin":idx+1}
			tmpSecuenciaMasLargaPos[pos.text] = {"inicio":idx+1,"fin":idx+1}
		
		if(ner != None):
			if(ner.text in cuentaNer.keys()):
				cuentaNer[ner.text] += 1
				ultimoLugarNer[ner.text] = idx+1
				if(tmpSecuenciaMasLargaNer[ner.text]["fin"] == idx):
					#secuenciaMasLargaNer[ner.text]["fin"] = idx+1
					tmpSecuenciaMasLargaNer[ner.text]["fin"] = idx+1
					if((secuenciaMasLargaNer[ner.text]["fin"]-secuenciaMasLargaNer[ner.text]["inicio"])<(tmpSecuenciaMasLargaNer[ner.text]["fin"]-tmpSecuenciaMasLargaNer[ner.text]["inicio"])):
						secuenciaMasLargaNer[ner.text]["fin"] = tmpSecuenciaMasLargaNer[ner.text]["fin"]
						secuenciaMasLargaNer[ner.text]["inicio"] = tmpSecuenciaMasLargaNer[ner.text]["inicio"]
			else:
				cuentaNer[ner.text] = 1
				primerLugarNer[ner.text] = idx+1
				secuenciaMasLargaNer[ner.text] = {"inicio":idx+1,"fin":idx+1}
				tmpSecuenciaMasLargaNer[ner.text] = {"inicio":idx+1,"fin":idx+1}
			if(normalizedNer != None):
				if(normalizedNer.tag != "sentiment"):
					if(normalizedNer.text in cuentaNormalizedNer.keys()):
						cuentaNormalizedNer[normalizedNer.text] += 1
					else:
						cuentaNormalizedNer[normalizedNer.text] = 1
	
	texto = ""
	texto += "<id>{}</id>".format(id)	
	texto += "<first-ner>{}</first-ner>".format(primerNer)
	texto += "<first-pos>{}</first-pos>".format(primerPos)
	for elemento in sorted(primerLugarNer.keys()):
		texto += "<first-place-{}-ner>{}</first-place-{}-ner>".format(elemento, primerLugarNer[elemento], elemento)
	for elemento in sorted(primerLugarPos.keys()):
		texto += "<first-place-{}-pos>{}</first-place-{}-pos>".format(elemento, primerLugarPos[elemento], elemento)
	for elemento in sorted(cuentaNer.keys()):
		texto += "<count-{}-ner>{}</count-{}-ner>".format(elemento, cuentaNer[elemento], elemento)
	for elemento in sorted(cuentaPos.keys()):
		texto += "<count-{}-pos>{}</count-{}-pos>".format(elemento, cuentaPos[elemento], elemento)
	if(len(cuentaNormalizedNer.keys())>0):
		texto += "<count-normalized-ner>"
		for idx, elemento in enumerate(sorted(cuentaNormalizedNer.keys())):
			if(idx == 0):
				texto += "{}:{}".format(str(elemento).replace(" ", "_"), cuentaNormalizedNer[elemento])
			else:
				texto += " {}:{}".format(str(elemento).replace(" ", "_"), cuentaNormalizedNer[elemento])
		texto += "</count-normalized-ner>"
	for elemento in sorted(ultimoLugarNer.keys()):
		texto += "<last-place-{}-ner>{}</last-place-{}-ner>".format(elemento, ultimoLugarNer[elemento], elemento)
	for elemento in sorted(ultimoLugarPos.keys()):
		texto += "<last-place-{}-pos>{}</last-place-{}-pos>".format(elemento, ultimoLugarPos[elemento], elemento)
	for elemento in sorted(secuenciaMasLargaNer.keys()):
		texto += "<longest-sequence-{}-ner>{}</longest-sequence-{}-ner>".format(elemento, secuenciaMasLargaNer[elemento]["fin"] - secuenciaMasLargaNer[elemento]["inicio"] + 1, elemento)	
	for elemento in sorted(secuenciaMasLargaPos.keys()):
		texto += "<longest-sequence-{}-pos>{}</longest-sequence-{}-pos>".format(elemento, secuenciaMasLargaPos[elemento]["fin"] - secuenciaMasLargaPos[elemento]["inicio"] + 1, elemento)
	
	print texto
with open("listaPos.txt","w") as archivo:
	for idx, pos in enumerate(posId):
		archivo.write("{} {}\n".format(idx, pos))

with open("listaNer.txt","w") as archivo:
	for idx, ner in enumerate(nerId):
		archivo.write("{} {}\n".format(idx, ner))