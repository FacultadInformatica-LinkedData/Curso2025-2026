# Instructions for assignment 4
Please follow the instructions below to successfully validate your assignments and do a pull request.

1. Synchronize your fork with the source repository: Go to YOUR fork in GitHub, and click on "Sync fork" like we did in class.
2. Pull the repository changes into your machine.
3. Work on the exercises. You can work in the notebooks in Colaboratory, as we did in class.  Mandatory exercises are `Task06.ipynb` and `Task07.ipynb`. Tasks 08 and 09 are **OPTIONAL**. Each mandatory exercise has a `validate_task` function that you can run to see whehter the exercise is providing a correct solution or not. You **must** run these cells while doing the exercises, although they will be checked automatically in your pull request.
4. Once you complete your assignment, you need to export a python script from your notebook. Do so by clicking on `File->Download->Download .py`.
5. **IMPORTANT** Comment the line `!pip install rdflib` in your python script (or any additional line with python magic).
6. Create a NEW folder in `Assignment4`. It should look like `Assignment4/YOURFOLDERNAME`, where `YOURFOLDERNAME` should be your name, last name and id. For example: `Assignment4/Daniel_Garijo_1234`
7. Place your python scripts only in that folder. Your scripts **must** be named `task0{NUMBER}.py`. For example, `task06.py`. If you don't follow this convention, your PR will fail. 
8. **COPY** the validation script (`validation.py`) in the same folder you put your assignments. You can find it in `Assignment4/course_materials/python/validation.py`. Therefore, if you submit the mandatory assignment, your PR should ONLY contain three files: `task06.py`, `task07.py` and `validation.py`.
9. Create a pull request to the main branch. A professor will activate an automated workflow on your scripts. If the workflow fails, your PR will be closed and you will need to review it, fix it and reopen it.
