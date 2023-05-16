import requests
from configparser import ConfigParser
import xml.etree.ElementTree as ET

dirDados = "C:\\Bancamais\\Fastcommerce\\DadosLoja"

with open("C:\\Bancamais\\Fastcommerce\\ProgramasExtras\\Conferência\\Stock-Check\\Resultado.txt", "w+") as f:
        pass

def output(info):
    with open("C:\\Bancamais\\Fastcommerce\\ProgramasExtras\\Conferência\\Stock-Check\\Resultado.txt", "a") as f:
        f.write(info)
        f.write("\n")
        f.close()

#Administração do arquivo .cfg
config_object = ConfigParser()
config_object.read(f"{dirDados}\\StoreData.cfg")
STOREINFO = config_object["STOREINFO"]
StoreName = STOREINFO["StoreName"]
StoreID = STOREINFO["StoreID"]
Username = STOREINFO["Username"]
password = STOREINFO["password"]

#Request
url = "https://www.rumo.com.br/sistema/adm/APILogon.asp"
payload= (f"""StoreName={StoreName}&StoreID={StoreID}&Username={Username}&
          method=ReportView&password={password}&ObjectID=425&Fields=IDProduto, Estoque""")
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

response = requests.request("POST", url, headers=headers, data=payload)

#Extrai os elementos do xml do fc
root = ET.fromstring(response.text)
produtos_fc = {}

for record in root.findall('Record'):
    id_produto = record.find('Field[@Name="IDProduto"]').attrib['Value']
    estoque = record.find('Field[@Name="Estoque"]').attrib['Value']
    produtos_fc[id_produto] = estoque


#Extrai os elementos do txt do b+
with open("C:\\Bancamais\\Fastcommerce\\ProgramasExtras\\Conferência\\Stock-Check\\syncEstoque.txt", "r") as r:
    file_contents = r.read()

produtos_bmais = {}

for line in file_contents.split('\n'):
    line = line.strip() 
    if not line:  
        break
    id_produto = line[0:8].strip() 
    estoque = line[8:].strip() 
    produtos_bmais[id_produto] = estoque

if len(produtos_bmais) != len(produtos_fc):
    output(f"DIVERGÊNCIA ENCONTRADA: A quantidade de produtos entre sistemas não é a mesma: [FC = {len(produtos_fc)} <-> B+ {len(produtos_bmais)}]")

c = 0

for key in produtos_bmais:
    try:
        if produtos_bmais[key] != produtos_fc[key]:
            output(f"Diferença de estoque encontrada: ID = {key} // B+ = {produtos_bmais[key]} <-> FC = {produtos_fc[key]}")
            c += 1
    except:
        output(f"Produto ID = {key} não encontrado no Fastcommerce.")

if c == 0:
    output("Nenhuma diferença encontrada.")
else:
    if c == 1:
        output("\n")
        output("Foi encontrada apenas 1 diferença de estoque em total.")
        output("\n")
    else:
        output("\n")
        output(f"Foram encontradas {c} diferenças de estoque em total.")
        output("\n")


if (response.text.find("<ErrCod>")) > 0:
    with open("C:\\Bancamais\\Fastcommerce\\ProgramasExtras\\Conferência\\Stock-Check\\Erro.txt", "w+") as e:
        e.write("Houve um erro ao checar os IDs.")
        e.write("\n")
        e.write(response.text)
        e.close()
