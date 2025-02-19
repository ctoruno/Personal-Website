---
author: Carlos A. Toruño P.
date: '2025-02-18'
draft: false
excerpt: >-
  A brief guide on how to perform a multiple impuytation on ordinal data using
  the MICE R package.
weight: 2
title: Multiple imputation with MICE on ordinal data
subtitle: A step-by-step guide
layout: single
tags:
  - ordinal data
  - missing data
  - mice
  - multiple imputation
---


<link href="mice_files/libs/htmltools-fill-0.5.8.1/fill.css" rel="stylesheet" />
<script src="mice_files/libs/htmlwidgets-1.6.4/htmlwidgets.js"></script>
<link href="mice_files/libs/datatables-css-0.0.0/datatables-crosstalk.css" rel="stylesheet" />
<script src="mice_files/libs/datatables-binding-0.33/datatables.js"></script>
<script src="mice_files/libs/jquery-3.6.0/jquery-3.6.0.min.js"></script>
<link href="mice_files/libs/dt-core-1.13.6/css/jquery.dataTables.min.css" rel="stylesheet" />
<link href="mice_files/libs/dt-core-1.13.6/css/jquery.dataTables.extra.css" rel="stylesheet" />
<script src="mice_files/libs/dt-core-1.13.6/js/jquery.dataTables.min.js"></script>
<link href="mice_files/libs/crosstalk-1.2.1/css/crosstalk.min.css" rel="stylesheet" />
<script src="mice_files/libs/crosstalk-1.2.1/js/crosstalk.min.js"></script>


<style>
  div.datatables.html-widget {
      width: 100%;
      height: auto;
      overflow-y: scroll;
  }
</style>

In [my last post](https://www.carlos-toruno.com/blog/clustering-public-opinion/00-intro/), I talked about a recent exercise that I performed in order to group people into clusters according to their opinions and perceptions regarding the state of the Rule of Law, Justice, and Governance in their countries and/or local regions. Due to the nature of the data, we will have to face the decision of what to do with the missing values that we have in our data set. And that... might not be an easy task.

The data I'm working with comes from a survey applied to the general public and has two important features. First, all questions I'm focusing on in this exercise offered the possibility to either refused to answer or say "_Don't know_", which is a completely valid answer. Second, all questions are measured as Liker scales, which is a specific form of ordinal data. As mentioned in the previous post, ordinal data has specific traits that makes the typical assumptions of linearity and normality to be invalid. These assumptions are very common for most data imputations out there. Therefore, you need to be very careful on which methods you are using to impute your data when facing ordinal data like I am right now.

There are a few options for you to choose when dealing with ordinal data, but the one I will be working on right now is a method called **_Multiple Imputation by Chained Equations (MICE)_**. In this post, I will be providing a step-by-step guide on how to perform this method in R on an example data set.

<img src="featured2.png" width="100%"/>

## What's MICE?

MICE is the use of a technique called Fully Conditional Specification (FCS) to the specific use case of handling missing data. The logic (and main assumption) behind MICE is that the information required to make a good educated guess for imputing the missing data is found within the data itself. Because of this, the imputation is performed by iteratively modeling each variable with missing data as a function of the other variables in the data set. MICE uses separate models for each variable and imputes missing values conditionally on the others. This process is repeated for all variables with missing data in an iterative fashion, cycling through them multiple times to refine the imputations and produce a "_complete_" data set.

The process can be summarized in 5 steps:

#### 1. Initialization

You start by replacing all the missing values in your data with a placeholder. There are two common strategies in this regard. first, you could replace them using the mean, median, or mode of their respective distribution. Second, you can use a random draw from the observed distribution. These methods are called **_univariate imputation_** because they only take into account the distribution of the variable at hand. For this specific example, I'm using the mean as a placeholder for my initialization step. This initial data

#### 2. Predictive model selection

You choose a predictive model based on the type of data you are handling. Given that our data consists in ordinal data, I'm choosing to use a **_Proportional Odds Logistic Regression_** (polr) which will be supplied by the [MASS package in R](https://www.stats.ox.ac.uk/pub/MASS4/). For continuous data, an OLS regression will be sufficient, and for binary variables a logistic regression will also be enough. Either way, you can choose your desired method as the base predictive model.

#### 3. Multivariate imputation

You choose one of the variables in your data set that you would like to perform the imputation on. Then, you model the observed values of that target variable (i.e. you remove the observations that have placeholders in that specific variable) as a function of the remaining set of features in your data set (including the placeholders). You use the predicted values as new placeholders for the target variable. It is important to note that, for the predicted values, the MICE algorithm introduces some sort of randomness adding a random error term to the predicted value. This error term is randomly drawn from the model's error distribution. You repeat this step for each one of the variables in your data set until you replace the initial placeholders for their predicted values.

#### 4. Iterative imputation

You repeat the multivariate imputation process multiple times. With each iteration, imputation improves as the predicted model is "_better informed_" by updated values from other variables. Ideally, you would like to stop the iterative process when you reach convergence, in other words, when the difference between the updated placeholders from the latest iteration and the placeholders from the previous one is very small.

#### 5. Multiple imputations

Once your process reach convergence, you have generated one "_complete_" data sets. However, you remember that random error term that I mentioned in step 3? Well, to account for the uncertainty in imputations you now want to reproduce the whole process again and produce multiple "_complete_" data sets.

If my explanation was not enough, I personally found the following video quite helpful. However, please take into account that this video does not cover the randomness in the imputation nor the production of several "complete" data sets:

<iframe width="100%" height="315" src="https://www.youtube.com/embed/WPiYOS3qK70?si=BAYRKUoHXkpvbtal" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
</iframe>

## Practical example

For this example, we will be using the following R libraries so make sure to have them installed before proceeding with the rest of this exercise:

``` r
library(DT)
library(glue)
library(mice)
library(MASS)
library(haven)
library(tidyverse)
```

The main package that we will be using for this exercise is the [MICE R package](https://amices.org/mice/) written by Stef van Buuren. The author has provided excellent documentation resources on how to perform MICE with this R package and has compiled all this documentation to be available available in his book [Flexible Imputation of missing Data](https://stefvanbuuren.name/fimd/), which I would highly suggest you to read.

### Let's take a look into our data

The data that I will be using is a mock subset of the [People's Voices data used in the WJP Eurovoices project](https://eurovoices.worldjusticeproject.org/peoples-voices). We start this routine by loading our data in our R Studio session:

``` r
df <- read_csv(
  file = "data_sample.csv",
  show_col_types = FALSE
)

print(
  glue(
    "Our data frame has {dim(df)[1]} rows(respondents) and {dim(df)[2]} columns (variables)!"
  )
)
```

    Our data frame has 15641 rows(respondents) and 29 columns (variables)!

``` r
datatable(df[sample(1:nrow(df), 10), ])
```

<div class="datatables html-widget html-fill-item" id="htmlwidget-e71abe8105448d830804" style="width:100%;height:auto;"></div>
<script type="application/json" data-for="htmlwidget-e71abe8105448d830804">{"x":{"filter":"none","vertical":false,"data":[["1","2","3","4","5","6","7","8","9","10"],["x006","x049","x058","x097","x086","x059","x059","x057","x078","x102"],[1,1,2,1,1,1,1,1,1,2],[1,1,2,1,2,1,2,2,1,1],[42,56,48,48,28,64,70,68,73,26],[1,1,1,1,1,1,1,1,1,1],[5,7,4,5,4,5,4,5,4,5],[2,1,null,5,4,4,2,4,5,3],[4,3,3,4,3,4,3,4,5,3],[1,3,1,1,1,6,6,6,8,1],[1,4,3,3,1,3,5,3,2,2],[4,2,5,3,3,2,1,3,3,6],[3,1,3,2,3,0,0,0,1,2],[2,3,3,2,4,1,3,3,2,3],[7,5,4,7,6,10,5,7,8,7],["BA","BA","BA","BA","BA","BA","BA","BA","BA","BA"],[2,4,2,2,3,1,2,3,2,4],[2,4,2,2,3,1,3,2,1,4],[2,4,2,2,null,1,2,2,1,4],[1,1,1,1,2,2,1,2,2,1],[2,1,2,2,2,2,3,2,2,2],[2,2,3,2,2,2,3,2,2,3],[2,2,2,2,2,2,3,2,2,3],[2,2,2,2,2,1,2,2,2,3],[2,1,2,2,2,1,4,2,2,2],[2,3,3,2,2,2,2,null,2,2],[2,2,2,2,2,1,1,null,2,null],[1,1,2,2,2,1,1,2,3,2],[1,1,2,2,2,2,1,1,3,3],[1,1,2,2,2,1,2,1,3,3]],"container":"<table class=\"display\">\n  <thead>\n    <tr>\n      <th> <\/th>\n      <th>regionid<\/th>\n      <th>urban<\/th>\n      <th>gend<\/th>\n      <th>age<\/th>\n      <th>nation<\/th>\n      <th>edu<\/th>\n      <th>income_quintile<\/th>\n      <th>fin<\/th>\n      <th>emp<\/th>\n      <th>marital<\/th>\n      <th>A1<\/th>\n      <th>A7<\/th>\n      <th>politics<\/th>\n      <th>polid<\/th>\n      <th>group<\/th>\n      <th>LEP_accountability<\/th>\n      <th>LEP_bribesreq<\/th>\n      <th>LEP_bribesacc<\/th>\n      <th>ROL_abusepower_imp<\/th>\n      <th>CPB_freemedia<\/th>\n      <th>CPB_freexp_cso<\/th>\n      <th>CPB_freexp_pp<\/th>\n      <th>CPB_freexp<\/th>\n      <th>CPB_freeassem<\/th>\n      <th>PAB_blamesoc<\/th>\n      <th>PAB_attackopp<\/th>\n      <th>ROL_courtrulings_imp<\/th>\n      <th>ROL_indgovtbodies_imp<\/th>\n      <th>ROL_csoinput_imp<\/th>\n    <\/tr>\n  <\/thead>\n<\/table>","options":{"columnDefs":[{"className":"dt-right","targets":[2,3,4,5,6,7,8,9,10,11,12,13,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29]},{"orderable":false,"targets":0},{"name":" ","targets":0},{"name":"regionid","targets":1},{"name":"urban","targets":2},{"name":"gend","targets":3},{"name":"age","targets":4},{"name":"nation","targets":5},{"name":"edu","targets":6},{"name":"income_quintile","targets":7},{"name":"fin","targets":8},{"name":"emp","targets":9},{"name":"marital","targets":10},{"name":"A1","targets":11},{"name":"A7","targets":12},{"name":"politics","targets":13},{"name":"polid","targets":14},{"name":"group","targets":15},{"name":"LEP_accountability","targets":16},{"name":"LEP_bribesreq","targets":17},{"name":"LEP_bribesacc","targets":18},{"name":"ROL_abusepower_imp","targets":19},{"name":"CPB_freemedia","targets":20},{"name":"CPB_freexp_cso","targets":21},{"name":"CPB_freexp_pp","targets":22},{"name":"CPB_freexp","targets":23},{"name":"CPB_freeassem","targets":24},{"name":"PAB_blamesoc","targets":25},{"name":"PAB_attackopp","targets":26},{"name":"ROL_courtrulings_imp","targets":27},{"name":"ROL_indgovtbodies_imp","targets":28},{"name":"ROL_csoinput_imp","targets":29}],"order":[],"autoWidth":false,"orderClasses":false}},"evals":[],"jsHooks":[]}</script>

As a rule of thumb, you don't want to perform a multiple imputation on variables that have over 15% of missing values. As we can see, we have some variables in our data frame that has over 2,000 missing values. However, all of them ar under this threshold. Nevertheless, we could remove some of them from this routine if we want to be more strict.


``` r
datatable(
  df %>%
  summarise(
    across(
      everything(),
      \(x) sum(is.na(x))
    )
  ) %>%
  pivot_longer(
    everything(),
    names_to  = "variable",
    values_to = "total_NAs"
  ) %>%
    arrange(desc(total_NAs)) %>%
    mutate(
      percentage_NAs = round((total_NAs/(dim(df)[1]))*100, 1)
    )
)
```

<div class="datatables html-widget html-fill-item" id="htmlwidget-f7a04a3c5e09ba53cfb4" style="width:100%;height:auto;"></div>
<script type="application/json" data-for="htmlwidget-f7a04a3c5e09ba53cfb4">{"x":{"filter":"none","vertical":false,"data":[["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29"],["LEP_bribesreq","LEP_bribesacc","PAB_blamesoc","income_quintile","PAB_attackopp","polid","LEP_accountability","ROL_indgovtbodies_imp","CPB_freemedia","ROL_csoinput_imp","CPB_freexp_cso","ROL_abusepower_imp","CPB_freexp_pp","ROL_courtrulings_imp","CPB_freeassem","CPB_freexp","fin","A7","politics","marital","emp","edu","nation","A1","age","regionid","urban","gend","group"],[2329,2320,2278,2241,1980,1915,1695,1613,1453,1410,1396,1181,1154,1144,839,618,449,253,172,129,119,72,41,14,8,0,0,0,0],[14.9,14.8,14.6,14.3,12.7,12.2,10.8,10.3,9.300000000000001,9,8.9,7.6,7.4,7.3,5.4,4,2.9,1.6,1.1,0.8,0.8,0.5,0.3,0.1,0.1,0,0,0,0]],"container":"<table class=\"display\">\n  <thead>\n    <tr>\n      <th> <\/th>\n      <th>variable<\/th>\n      <th>total_NAs<\/th>\n      <th>percentage_NAs<\/th>\n    <\/tr>\n  <\/thead>\n<\/table>","options":{"columnDefs":[{"className":"dt-right","targets":[2,3]},{"orderable":false,"targets":0},{"name":" ","targets":0},{"name":"variable","targets":1},{"name":"total_NAs","targets":2},{"name":"percentage_NAs","targets":3}],"order":[],"autoWidth":false,"orderClasses":false}},"evals":[],"jsHooks":[]}</script>

Something that you could have noticed is that the first 15 columns in our data are socio-demographics variables that are not necessary to impute for the purposes of our clustering exercise. I will be performing the MICE algorithm without these socio-demographic features. However, you should know that they can be included as features in the predictive model to further support the prediction process.

### Performing the imputation

We start that subsetting only for the variables of interest. It is very important that you declare your variables as ordered factors. I do this by applying the `ordered()` function across multiple variables. I specify either `levels = 1:4` or `levels = 1:3` depending on the number of points (answers) that each set of variable has.

``` r
# List of socio-demographic predictors
demographic_predictors <- c(
  "regionid", "urban", "gend", "age", "nation", "edu", 
  "income_quintile", "fin", "emp", "marital", "A1", "A7",
  "politics", "polid",
  "group"
)

# Subsetting and defining variable types
df_nodems <- df %>%
  dplyr::select(-demographic_predictors) %>%
  mutate(
    
    # Defining variable types
    across(
      all_of(c(
         "LEP_accountability", "LEP_bribesreq", "LEP_bribesacc", "CPB_freemedia",
         "CPB_freexp_cso", "CPB_freexp_pp", "CPB_freexp", "CPB_freeassem", "PAB_blamesoc",
         "PAB_attackopp" 
      )),
      \(x) ordered(x, levels = 1:4)
    ),
    across(
      all_of(ends_with("_imp")),
      \(x) ordered(x, levels = 1:3)
    )
  )
```

Once we have defined a data frame to work with, we use the `mice()` function to perfom the multiple imputation. The argument `m` defines the number of imputations that you want to perform (defined as step 5 above). `maxit` defines a maximum number of iterations in your process (defined as step 4 above). Given that all of our features are ordered variables, I pass a single string to `method = "polr"`. If you happen to have a combination of ordered, binary response, and continuous variables, then you would have to pass a vector of strings specifying the methods that you wish to use. For example, "pmm" for predictive mean matching, "logreg" for logistic regression, "rf" for random forest, and so on. You should check the documentation to see which methods are available. Finally, I also added a `seed = 1910` (which is my mom's birthday) so my results are reproducible (remember the randomness that you are introducing in your imputations).

``` r
imputed <- mice::mice(
  data   = df_nodems,
  m      = 5,
  maxit  = 10,
  method = "polr",
  seed   = 1910,
  print  = FALSE
)
```

The result returned by `mice()` is an object of class "mids", which stands for Multiply Imputed Data Set. This object has all the information generated during the multiple imputation process, including your "_complete_" data sets. To access these data sets, you will have to make use of the `complete()` function as follows:

``` r
complete_df_1 <- mice::complete(imputed, action = 1)
```

You only need to pass the mids object returned by `mice()` and define an action number. The action number is equivalent to the number of imputations that you requested. For example, when I executed `mice()`, I specified `m=5`. Therefore, the mids object has 5 different "_complete_" data sets stored. Therefore, you can access each one of these data frames by defining $action = 1, 2,..., m=5$. Additionally, you could define `action=0` to access the pre-imputation data frame.

Let's see the amount of missing values in this new data frame:

``` r
datatable(
  complete_df_1 %>%
  summarise(
    across(
      everything(),
      \(x) sum(is.na(x))
    )
  ) %>%
  pivot_longer(
    everything(),
    names_to  = "variable",
    values_to = "total_NAs"
  ) %>%
    arrange(desc(total_NAs)) %>%
    mutate(
      percentage_NAs = round((total_NAs/(dim(df)[1]))*100, 1)
    )
)
```

<div class="datatables html-widget html-fill-item" id="htmlwidget-67be73901626e7b5c0fe" style="width:100%;height:auto;"></div>
<script type="application/json" data-for="htmlwidget-67be73901626e7b5c0fe">{"x":{"filter":"none","vertical":false,"data":[["1","2","3","4","5","6","7","8","9","10","11","12","13","14"],["LEP_accountability","LEP_bribesreq","LEP_bribesacc","ROL_abusepower_imp","CPB_freemedia","CPB_freexp_cso","CPB_freexp_pp","CPB_freexp","CPB_freeassem","PAB_blamesoc","PAB_attackopp","ROL_courtrulings_imp","ROL_indgovtbodies_imp","ROL_csoinput_imp"],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]],"container":"<table class=\"display\">\n  <thead>\n    <tr>\n      <th> <\/th>\n      <th>variable<\/th>\n      <th>total_NAs<\/th>\n      <th>percentage_NAs<\/th>\n    <\/tr>\n  <\/thead>\n<\/table>","options":{"columnDefs":[{"className":"dt-right","targets":[2,3]},{"orderable":false,"targets":0},{"name":" ","targets":0},{"name":"variable","targets":1},{"name":"total_NAs","targets":2},{"name":"percentage_NAs","targets":3}],"order":[],"autoWidth":false,"orderClasses":false}},"evals":[],"jsHooks":[]}</script>

As we can observe, after 10 iterations, the algorithm was able to successfully impute all the missing values that we initially had through educated guesses based on the relationships between the variables that we included in the analysis. The question that you might have now is how to proceed with the main analysis now that you have 5 different data sets instead of just one. Well, [as suggested in the book](https://stefvanbuuren.name/fimd/workflow.html), you should now perform the analysis you had in mind multiple times on each "_complete_" data set and then pool your results, using Rubin's Rules if possible. Actually, they have a nice infographic portraying their suggested workflow:

<img src="wflow.png" width="100%"/>

The MICE package also comes along with a set of handy functions suchs as `with()` and `pool()`. The first one allows you to perform the statistical analysis on each one of these imputed data sets while the second ones performs the pooling of results for you. For example, let's say that I would like to fit a linear regression of `PAB_blamesoc` as a funtion of `CPB_freemedia`, `LEP_bribesacc`, and `PAB_attackopp`. In that case i could proceed as follows:

``` r
fit <- imputed %>%
  with(
    lm(as.formula("PAB_blamesoc ~ CPB_freemedia + LEP_bribesacc"))
  ) %>%
  pool()

summary(fit)[1:2]
```

                 term     estimate
    1     (Intercept)  2.203141115
    2 CPB_freemedia.L -0.470263363
    3 CPB_freemedia.Q -0.028115584
    4 CPB_freemedia.C  0.004979305
    5 LEP_bribesacc.L -0.070947210
    6 LEP_bribesacc.Q  0.060894583
    7 LEP_bribesacc.C  0.043139297

Finally, as you can imagine, running a MICE algorithm can require a lot of computing power depending on the size on your data dimensions, the number of iterations, and also the number of imputations that you want to perform. Lucky fo us, the MICE package also offers a `futuremice()` function that allows you to compute the imputation on several instances of R using the [future R package](https://future.futureverse.org/). I'm running these computation on a Macbook Pro with 16 CPU cores, therefore, I decided to allocate 5 cores to this computation (1 per imputation) by setting `n.core=5`.

You just need to remember two things. First, you need to set up a `parallelseed` rather than a `seed`. This is because `futuremice()` will start a different instance of R for each imputation, and if you set a seed, each instance will follow the same quasi-random path defined in your `seed`, loosing the randomness that you are trying to account for. Second, once your `futuremice()` finish working, don't forget to return your `future::plan()` back to sequential. For more information on plans and how they affect your computation, you can check \[this link\](https://future.futureverse.org/articles/future-1-overview.html#controlling-how-futures-are-resolved.

``` r
imputed <- mice::futuremice(
  data   = df_nodems,
  m      = 5,
  maxit  = 10,
  method = "polr",
  # seed   = 1910,
  n.core = 5,
  parallelseed = 1910,
  print  = FALSE
)
future::sequential()
```

And that's basically it. Hasta la próxima mi gente!
