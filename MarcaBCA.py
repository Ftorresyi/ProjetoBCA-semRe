#FUNÇÃO LÊ O BCA E MARCA AS OM'S APOIADAS E PRINCIPAIS MATÉRIAS DE LEITURA

#ATENTAR PARA O DETALHE DE QUE FOI USADA A VERSÃO PyMuPDF==1.18.19 PARA QUE O FITZ FUNCIONASSE CORRETAMENTE
#POIS A FUNÇÃO HIGHLIGHT NÃO FUNCIONA CORRETAMENTE NA VERSÃO ATUAL (PyMuPDF==1.20)

#Instalar os requisitos:
#$ pip install PyMuPDF==1.18.19

from typing import Tuple
import io
import os
import argparse
import re
import fitz
import string
from datetime import date
from unidecode import unidecode


#LISTA DAS PALAVRAS QUE PRECISAM SER BUSCADAS NO PDF "bcadodia.PDF"
lista_OMs=[
  'GAP GL','GAP-GL','GRUPAMENTO DE APOIO DO GALEÃO','GAPGL',
  'PAMA GL','PAMA-GL','PARQUE DE MATERIAL AERONÁUTICO DO GALEÃO','PAMA GL','PAMAGL', 
  'BAGL','BASE AÉREA DO GALEÃO','BAGL_ANTIGA',
  '1 CJM','1CJM','PRIMEIRA CIRCUNSCRIÇÃO JUDICIÁRIA MILITAR','1°CJM','1° CJM','1ºCJM','1º CJM',
  'CEMAL','CENTRO DE MEDICINA AEROESPACIAL',    
  'BINFAE GL','BINFAE-GL','BATALHÃO DE INFANTARIA DA AERONÁUTICA ESPECIAL DO GALEÃO','BINFAEGL',
  'CCA RJ','CENTRO DE COMPUTAÇÃO DA AERONÁUTICA DO RIO DE JANEIRO','CCARJ', 'CCA-RJ',    
  'PAGL','PREFEITURA DE AERONÁUTICA DO GALEÃO',
  '3 ETA','TERCEIRO ETA','3ETA','3° ETA','3°ETA','3ºETA','3º ETA',
  'GOP GL','GOP-GL','GRUPO OPERACIONAL DO GALEÃO','GOPGL','GOPGL',
  'GLOG GL','GLOG-GL','GRUPO LOGÍSTICO DO GALEÃO','GLOGGL',
  'MTAB','MISSÃO TÉCNICA AERONÁUTICA BRASILEIRA NA BOLÍVIA',
  'DIRAP','DIRETORIA DE ADMINISTRAÇÃO DO PESSOAL',
  'DIRSA','DIRETORIA DE SAÚDE DA AERONÁUTICA', '/DIRSA',
  'CGABEG','CENTRO GERONTOLÓGICO DE AERONÁUTICA BRIGADEIRO EDUARDO GOMES',
  'CBNB','COLÉGIO BRIGADEIRO NEWTON BRAGA',
  'SERIPA III','TERCEIRO SERVIÇO REGIONAL DE INVESTIGAÇÃO E PREVENÇÃO DE ACIDENTES AERONÁUTICOS','SERIPAIII',
  ' ESG','ESCOLA SUPERIOR DE GUERRA',
  'PAMB RJ','PAMB-RJ','PARQUE DE MATERIAL BÉLICO DE AERONÁUTICA DO RIO DE JANEIRO','PAMBRJ',
  'DTCEA-GL','DTCEA GL','DESTACAMENTO DE CONTROLE DO ESPAÇO AÉREO DO GALEÃO','DTCEAGL',
  '1/2 GT','1°/2° GT','1°/2°GT','PRIMEIRO ESQUADRÃO DO SEGUNDO GRUPO DE TRANSPORTE','1/2GT','1°/2°GT','1º/2º GT','1º/2ºGT',
  '1GCC','1 GCC','PRIMEIRO GRUPO DE COMUNICAÇÕES E CONTROLE','1° GCC','1°GCC','1ºGCC','1º GCC', '/1 GCC',
  '1/1 GT','1°/1° GT','1°/1°GT','PRIMEIRO ESQUADRÃO DO PRIMEIRO GRUPO DE TRANSPORTE','1/1 GT',r'1?/1? GT',r'1?/1?GT', 
  '2/2 GT','2°/2° GT','2°/2°GT','SEGUNDO ESQUADRÃO DO SEGUNDO GRUPO DE TRANSPORTE','2°/2°GT','2/2GT','2º/2º GT','2º/2ºGT',
  'LAQFA','LABORATÓRIO QUÍMICO-FARMACÊUTICO DE AERONÁUTICA',
  'CTLA','CENTRO DE TRANSPORTE LOGÍSTICO DE AERONÁUTICA',
  'ALA 11','BASE AÉREA DO GALEÃO','ALA11',
  'CIMAER','CENTRO INTEGRADO DE METEOROLOGIA DE AERONÁUTICA',
  ' CAE ','CENTRO DE AQUISIÇÕES ESPECÍFICAS',' CAE/', '/CAE',
  'COPE-S','CENTRO DE OPERAÇÕES ESPACIAIS SECUNDÁRIO','COPE S',
  'GSD-GL','GRUPO DE SEGURANÇA E DEFESA DO GALEÃO','GSDGL',
  'hfag','HOSPITAL DE FORÇA AÉREA DO GALEÃO',]

#OMs= [unidecode(padrao.upper()) for padrao in lista_OMs] #remove os acentos das OMs da lista e transforma em letras maiúsculas
#print(OMs) #Teste ->Até aqui tudo OK

#Arquivo principal do BCA em PDF que será usado:
BCAemPDF=input("Digite o nome do arquivo BCA que será lido, sem a extensão: ")+".pdf"


def normaliza(palavra):
  #Remover acentos
  palavra = unidecode(palavra)
  #Converter para maiúsculas:
  palavra=palavra.upper()
  #Remover espaços em branco:
  palavra=palavra.strip()
  #Remover pontuação:
  palavra=''.join(ch for ch in palavra if ch not in string.punctuation)
  return palavra

#Normalizar todas as palavras da lista de OMs
OMs = [normaliza(palavra) for palavra in lista_OMs]

#Normalizar as palavras do PDF:
palavras_normalizadas = []
pdf = fitz.open(BCAemPDF)
for page in pdf:
  texto = page.getText() #extrai o texto da página
  palavras = texto.split() #cria uma lista de palavras com o texto de cada página
  #Normaliza cada palavra e adiciona à lista de palavras normalizadas:
  for palavra in palavras:
    palavras_normalizadas.append(normaliza(palavra))


#LISTA DAS PALAVRAS QUE DEVERÃO SER DESMARCADAS:
PalavrasChave=[' PORTARIA DIRAP ', ' da PORTARIA ', '\tPortaria Dirap n', '\nPortaria DIRAP n°', 'Subdiretor Interino de Pessoal Militar da Dirap', 
'Subdiretor Interino de Pessoal Civil da Dirap', '/DIRAP',  'DIRAP nº', ' DIRAP Nº ', 'Portaria DIRSA', 'Portaria DIRSA nº']


sumannot = 0
def MarcaOMsApoiadas(*args):
  BcadoDia = fitz.open(*args)
  #BcadoDia= TrataArquivo(*args)
  global sumannot
  #file1 = io.open('texto-maiusculo.txt', 'w', encoding='utf-8')
  for page in BcadoDia: #loop para busca pagina a pagina dentro do BcadoDia
    for i in OMs:   #loop busca OM por OM da lista OMs em cada pagina do BcadoDia
      text_instances = page.search_for(i)  # text_instances recebe a busca da lista de OMs em todas as paginas  
      if text_instances != []:  #Se a lista de OMs nao for vazia    
        for inst in text_instances: #Percorre a lista de palavras achadas uma a uma 
          highlight = page.addHighlightAnnot(inst) #marca a palavra da lista de achadas
          print('Foi encontrada a palavra: ', highlight) #imprime a palavra marcada que eh um objeto da classe Fitz
          sumannot = sumannot + 1 #incrementa o contador de palavras encontradas
  #file1.close()
  print('Foram encontradas: ', sumannot, ' anotações no total')
  BcadoDia.save("bca_do_dia_marcado.pdf")


nannot=0
def removeHighlightv2(pdf_marcado, palavras_para_desmarcar):
  BcadoDia = fitz.open(pdf_marcado)
  global nannot
  for page in BcadoDia:
    #procuro pelas palavras que devem ser desmarcadas
    for palavra in palavras_para_desmarcar:
      text_instances = page.search_for(palavra)
      if len(text_instances) > 0: #é melhor comparar assim
      #se tiver encontrado algo, significa que provavelmente nessa pagina há alguma coisa que
      # foi marcada e não deveria ter sido marcada e agora será desmarcada
        for inst in text_instances:
          #para cada palavra que foi marcada, irei buscar todas as anotacoes
          #e verificar se há intercessão entre a anotação e aquilo que não deveria estar anotado
          for annot in page.annots():
            if (inst.intersect(annot.rect)):
              print("Remove anotacao ", palavra ," pg", page.number)
              page.delete_annot(annot)
              nannot=nannot+1
  print('Foram removidas ', nannot, ' anotações')
  BcadoDia.save("Marcado_"+ os.path.basename(BCAemPDF))
  

#data_atual = str(date.today())
#nBCA=input('Digite o número do BCA que será lido: ')
#dataBCA=input('Digite a data do BCA: ')
MarcaOMsApoiadas(BCAemPDF)
removeHighlightv2('bca_do_dia_marcado.pdf', PalavrasChave)
print('O Total de palavras encontradas para transcrição são: ', sumannot-nannot)
os.remove("bca_do_dia_marcado.pdf")



""" def TrataArquivo(arquivo): #função que trata o arquivo e retorna o conteúdo do arquivo
  arquivo=fitz.open(arquivo)
  for page in arquivo:
    text_instance = page.get_text().upper()#transforma o texto em maúsculo
    text_instance = unidecode(text_instance)#Remove os acentos das palavras
    newPdf = page.newPage()#cria uma nova página
    page.insertText(text_instance)
    #arquivo.write(text_instance) # TESTE de visualizacao - salva os dados do texto em maiúsculo no arquivo file1
  newPdf.save()
TrataArquivo('bca_176_25-09-2023.pdf') """