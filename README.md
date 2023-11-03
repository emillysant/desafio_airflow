# Indicium Airflow Hands-on Tutorial

## O Problema

Vamos utilizar o mesmo problema do desafio de data engineering do processo seletivo da indicium:

https://github.com/techindicium/code-challenge

Básicamente precisamos extrair os dados do banco northwind(banco demo de ecommerce) para hd local primeiro, e depois do hd para um segundo banco de dados. Também precisamos fazer load de um arquivo com informação de vendas que por algum motivo vem de outro sistema em um arquivo csv. 

Com esses dados juntos em um database, gostariamos de saber quanto foi vendido em um dia

O pipeline vai ficar algo parecido com o seguinte:

![image](https://user-images.githubusercontent.com/49417424/105993225-e2aefb00-6084-11eb-96af-3ec3716b151a.png)

e os dados no hd devem ficar parecido com o segundo esquema:

```
/data/postgres/{table}/2021-01-01/file.format
/data/postgres/{table}/2021-01-02/file.format
/data/csv/2021-01-02/file.format
```

## Iniciando projeto

Primeiro passo foi fazer o download do arquivo no bitbucket
```git clone git@bitbucket.org:indiciumtech/airflow_tooltorial.git```

Entrar na pasta do projeto
```cd airflow_tooltorial```

criar uma venv
```virtualenv venv -p python3```

executar a venv
```source venv/bin/activate```

executar
```python3 install.sh```


## Limpando os Dags de Exemplo

Para tirar os dags de exemplo e começar um dag nosso, podemos apagar os arquivos
airflow-data/data e airflow-data/admin-password.txt, e editar o arquivo airflow.cfg trocando:
```
load_examples = True
```
para
```
load_examples = False
```
e
``` ags_folder = /home/emilly/airflow_tooltorial/dags```


Na sequência rodamos o comando para resetar o db do airflow e fazer start do airflow local:

```
airflow db reset
airflow standalone
```

## Rodando a dag do desafio

Ir em install.sh e mudar 
``` export AIRFLOW_HOME=/home/emilly/airflow_tooltorial```

pode executar tbm no terminal
``` export AIRFLOW_HOME=/home/emilly/airflow_tooltorial```

Depois de escrever as task dentro do arquivo dags/example_desafio.py exeutar pipeline do desafio
```airflow db reset```
```airflow standalone```

Ir em http://localhost:8080 e visualizar a dag do desafio: 
![Captura de tela de 2023-10-31 19-28-39](https://github.com/emillysant/desafio_airflow/assets/70452464/cd0bfc46-1274-4dd2-8594-402e43036f16)

## Adicionar uma variável no Airflow 
com a key "my_email" e no campo "value" adicionei meu email @indicium.tech.

## Definindo as tasks
Escrevendo as tasks dentro do arquivo example_desafio.py

### Task1
Criar uma task que lê os dados da tabela 'Order' do banco de dados disponível em data/Northwhind_small.sqlite. O formato do banco de dados é o Sqlite3. Essa task escrever um arquivo chamado "output_orders.csv".
Obs: ds_nodash nos ajuda a organizar o output por dia de execução. imprimindo junto a data
Declarar a função: 
```
def extract_order_data(**context):
    conn = sqlite3.connect('./data/Northwind_small.sqlite')
    order_df = pd.read_sql_query('SELECT * from "Order";', conn)
    order_df.to_csv(f"data/output_orders{context['ds_nodash']}.csv")
    conn.close()
```
Dentro da Dag declarar a task1: 
```
    extract_order_data_task = PythonOperator (
        task_id = 'extract_order_data_task',
        python_callable=extract_order_data,
        provide_context=True
    )
```

Obs: ds_nodash nos ajuda a organizar o output por dia de execução. imprimindo junto a data

![Captura de tela de 2023-11-03 16-25-30](https://github.com/emillysant/desafio_airflow/assets/70452464/177357b0-7219-4ff4-9633-5f97ef662edb)

### Task2
Criar uma task que lê os dados da tabela "OrderDetail" do mesmo banco de dados e faz um JOIN com o arquivo "output_orders.csv" que você exportou na tarefa anterior. Essa task calcula qual a soma da quantidade vendida (Quantity) com destino (ShipCity) para o Rio de Janeiro. Por fim exportar essa contagem em arquivo "count.txt" que contenha somente esse valor em formato texto (use a função str() para converter número em texto)

Declarar a função: 
```
def calculate_rio_quantity(**context):
    conn = sqlite3.connect('./data/Northwind_small.sqlite')
    orderDetail_df = pd.read_sql_query('SELECT * from "OrderDetail";', conn)
    order_df = pd.read_csv(f"data/output_orders{context['ds_nodash']}.csv")
    merge_df = pd.merge(orderDetail_df, order_df, how="inner", left_on="OrderId", right_on="Id")
    finds_Rio_df = merge_df.query('ShipCity == "Rio de Janeiro"')
    count = str(finds_Rio_df['Quantity'].sum())
    with open("count.txt", 'w') as f:
        f.write(count)
    conn.close()
```
Declara a task2 dentro da dag: 
```
    calculate_rio_quantity_task = PythonOperator (
        task_id = 'calculate_rio_quantity_task',
        python_callable=calculate_rio_quantity,
        provide_context=True
    )
```
## Criar uma ordenação de execução das Tasks que deve terminar com a task export_final_output:

```
extract_order_data_task >> calculate_rio_quantity_task >> export_final_output
```

## Executando a Dag
No terminal
``` export AIRFLOW_HOME=/home/emilly/airflow_tooltorial```
``` airflow standalone```

Acesse a porta 8080:  http://localhost:8080

Fazer login com as informações do terminal.
```
standalone | 
standalone | Airflow is ready
standalone | Login with username: admin  password: ******
standalone | Airflow Standalone is for development purposes only. Do not use this in production!
standalone |

```
Clique na dag do desafio 

Clique na seta do lado direito --> Trigger Dag para executar sua DAG


