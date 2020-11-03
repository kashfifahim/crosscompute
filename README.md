# CrossCompute

Publish your tool by writing a configuration file.

Please see https://crosscompute.com for examples and tutorials.

```bash
# pip install -U crosscompute
pip install https://github.com/crosscompute/crosscompute

# export CROSSCOMPUTE_CLIENT=https://crosscompute.com
# export CROSSCOMPUTE_SERVER=https://services.crosscompute.com
export CROSSCOMPUTE_TOKEN=YOUR-TOKEN
```

## See Project

```
crosscompute projects see
crosscompute projects see | jq
crosscompute projects see | jq '.[] | {id:.id, name:.name}'
crosscompute projects see PROJECT-ID
```

## Add Project

```
crosscompute projects add --name "Project X"
```

## Change Project

```
crosscompute projects change PROJECT-ID \
    --datasetId abc \
    --toolId def \
    --toolId ghi \
    --resultId jkl \
    --resultId mno
```

## See Tool

```
crosscompute tools see
crosscompute tools see | jq
crosscompute tools see | jq .[].id
crosscompute tools see TOOL-ID
```

## Add Tool

```
cd ~/Documents
git clone git@github.com:crosscompute/crosscompute-examples
cd crosscompute-examples/add-numbers

# Mock
crosscompute tools add .crosscompute.yml --mock

# Real
crosscompute tools add .crosscompute.yml
```

## Add Result

```
crosscompute results add \
    result.json \
    --name RESULT-NAME \
    --toolId TOOL-ID \
    --toolVersionId TOOL-VERSION-ID \
    --projectId PROJECT-ID
```

## Run Worker

```
crosscompute workers run
```

## Acknowledgments

- Olga Creutzburg
- Salah Ahmed
- Rodrigo Guarachi
- Polina Chernomaz
- Marta Moreno
- Ning Wei
- Miguel Angel Gordián
- Noé Domínguez Porras
- Elaine Chan
- Jennifer Ruda
- Aida Shoydokova
