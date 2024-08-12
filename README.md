# Reproducibility Repository for: A Path-based Approach to Analyzing the Global Liner Shipping Network

This repository will contain code for the methods and analyses described in the following paper:

* LaRock, T., Xu, M., Eliassi-Rad, T. A Path-based Approach to Analyzing the Global Liner Shipping Network. [EPJ Data Science *11* (18)](https://doi.org/10.1140/epjds/s13688-022-00331-z), March 2022. [arxiv link](https://arxiv.org/abs/2110.11925).

The data used for our analyses are proprietary and provided by [Alphaliner](https://public.alphaliner.com/). Per the agreement under which the data were provided, we are not able to share the shipping routes themselves. Instead, we have developed and released a realistic set of synthetic routes that show similar characteristics to demonstrate our methodology in the `data/synthetic/` directory. Although unfortunately this means the work will not be fully reproducible, we will be able to demonstrate some of the most important results of our research, and prototype code for our minimum-route path computations is available at `code/iterative_minroutes.py`.

If you have any questions or requests, please either open an issue or contact Timothy LaRock [via email](mailto:timothylarock@gmail.com).
