# nbayes-generalized

## Dependencies

* Python >= 3.7
* PostgreSQL >= 13

## Use

```
$ pip install -r requirements.txt
$ python training.py
$ python validation.py
$ python plt_recall.py
```

## Directories and necessary data

* `data/`: Epidemiologic COVID-19 data from DGE (https://www.gob.mx/salud/acciones-y-programas/direccion-general-de-epidemiologia) and all set attributes partitions.  
* `results`: Epsilon and scores computations for each bayesian model.
* `recall_plots`: Recall plots generated from validation data.

## Author

* Pedro Romero Martinez (pedro.romero@c3.unam.mx)