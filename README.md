# Expansão do acesso à internet por meio da reciclagem de roteadores

Este repositório contém códigos e instruções para replicar os testes realizados no projeto.


## Gerando a imagem do OpenWrt

Baixe o [image builder](https://downloads.openwrt.org/releases/19.07.4/targets/ar71xx/tiny/openwrt-imagebuilder-19.07.4-ar71xx-tiny.Linux-x86_64.tar.xz), descompacte e monte uma imagem sem os utilitários de PPP, e substituindo o `wpad-mini` pelo `hostapd`:

```
make image PROFILE=tl-wr941nd-v5 PACKAGES="-ppp -ppp-mod-pppoe -luci-proto-ppp -wpad-mini hostapd"
```

Instale o OpenWrt como de costume: com o arquivo `factory` se for usar a ferramenta de atualização original do fabricante, ou com o arquivo `sysupgrade` se for atualizar um roteador que já tenha o OpenWrt instalado.


## Construindo o inventário de roteadores

Configure todos os roteadores com a sua chave pública SSH em `/etc/dropbear/authorized_keys`. O servidor SSH do OpenWrt é o Dropbear, portanto use uma chave do tipo RSA, que é suportada por ele.

Edite as configurações em [inventory.ini](cfg/inventory.ini). Crie uma seção com o IP de cada roteador. Caso queira aplicar um certo valor como padrão a todos os roteadores, adicione-o à seção `[DEFAULT]`.

Valores que devem ser mantidos em segredo podem ser configurados da mesma forma, mas no arquivo [secrets.ini](cfg/secrets.ini). Este repositório configura esse arquivo para ser protegido pelo [git-crypt](https://github.com/AGWA/git-crypt).


## Editando templates de configuração

Os templates de configuração devem ser listados em [templates.ini](cfg/templates.ini) no formato `arquivolocal=/arquivo/remoto`. Os arquivos locais devem ser escritos na [linguagem do Jinja2](https://jinja.palletsprojects.com/en/2.11.x/templates) e inseridos no diretório [templates](templates).


## Criando o virtualenv para as ferramentas Python

Execute:

```
virtualenv .venv
.venv/bin/pip install -r requirements.txt
```

## Aplicando configurações em massa

Execute:

```
.venv/bin/python -m wrtmgr apply_config
```

Para cada roteador, a ferramenta vai dar uma saída `[ok]` caso o roteador já contenha a configuração esperada, ou `[changed]` caso a configuração tenha sida alterada pela ferramenta.


## Monitorando os roteadores

Execute:

```
.venv/bin/python -m wrtmgr metrics_exporter
```

Isso vai executar um coletor de métricas compatível com Prometheus na porta 9890. É possível alterar a porta com a opção `--port` caso desejado.


## Executando o Prometheus

Uma vez que o coletor esteja executando, é possível configurá-lo em uma instância do Prometheus. O arquivo [prometheus.yml](prometheus.yml) contém um exemplo. Para executá-lo:

```
docker run --net=host -p 9090:9090 -v ./prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```

Depois disso, será possível acessar a interface do Prometheus em [http://localhost:9090](http://localhost:9090).

