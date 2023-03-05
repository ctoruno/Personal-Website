---
title: "Geocoding"
format: hugo-md
project:
  execute-dir: project
---

<script src="/rmarkdown-libs/htmlwidgets/htmlwidgets.js"></script>
<script src="/rmarkdown-libs/jquery/jquery.min.js"></script>
<link href="/rmarkdown-libs/leaflet/leaflet.css" rel="stylesheet" />
<script src="/rmarkdown-libs/leaflet/leaflet.js"></script>
<link href="/rmarkdown-libs/leafletfix/leafletfix.css" rel="stylesheet" />
<script src="/rmarkdown-libs/proj4/proj4.min.js"></script>
<script src="/rmarkdown-libs/Proj4Leaflet/proj4leaflet.js"></script>
<link href="/rmarkdown-libs/rstudio_leaflet/rstudio_leaflet.css" rel="stylesheet" />
<script src="/rmarkdown-libs/leaflet-binding/leaflet.js"></script>
<script src="/rmarkdown-libs/leaflet-providers/leaflet-providers_1.9.0.js"></script>
<script src="/rmarkdown-libs/leaflet-providers-plugin/leaflet-providers-plugin.js"></script>
<script src="/rmarkdown-libs/htmlwidgets/htmlwidgets.js"></script>
<script src="/rmarkdown-libs/jquery/jquery.min.js"></script>
<link href="/rmarkdown-libs/leaflet/leaflet.css" rel="stylesheet" />
<script src="/rmarkdown-libs/leaflet/leaflet.js"></script>
<link href="/rmarkdown-libs/leafletfix/leafletfix.css" rel="stylesheet" />
<script src="/rmarkdown-libs/proj4/proj4.min.js"></script>
<script src="/rmarkdown-libs/Proj4Leaflet/proj4leaflet.js"></script>
<link href="/rmarkdown-libs/rstudio_leaflet/rstudio_leaflet.css" rel="stylesheet" />
<script src="/rmarkdown-libs/leaflet-binding/leaflet.js"></script>
<script src="/rmarkdown-libs/leaflet-providers/leaflet-providers_1.9.0.js"></script>
<script src="/rmarkdown-libs/leaflet-providers-plugin/leaflet-providers-plugin.js"></script>

In the previous series of posts about Web Scraping, we extracted information about lawyers in Germany and Poland. Within that information, we were able to extract their addresses, which give us a lot of information about their location. Nevertheless, these text strings are just that… text. If we want to take advantage of this kind of information we need to be able to translate this text characters into geographical coordinates. This process of transforming the description of a location into a set of geographical coordinates is called **Geocoding**.

In this post, I will use information extracted from the [Austrian Bar Association](https://www.rechtsanwaelte.at/) to geocode and visualize the geographical distribution of lawyers across the country using R.

<img src="featured.png" width="100%"/>

## What’s Geocoding?

As mentioned before, **geocoding** is the process of transforming a description of a location into geographical coordinates such as longitude and latitude. Similarly, you can also perform reverse geocoding, which is the process of recognizing a set of geographical coordinates and provide an associated description about this location and how to reach it.

The most practical way to geocode huge volumes of information is to access the data sets of online mapping services like Google Maps or OpenStreetMap through an API. If you want to know more about such services, I would suggest you check the following video by Google:

<iframe width="100%" height="325" src="https://www.youtube.com/embed/2IIhGA1cfmc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
</iframe>

Even thogh Google Maps is the most famous mapping provider out there, in this post I will be showing you how to geocode Austrian location using the Open Street Map (OSM) API. Why? First of all, because their services are freely available through their Nominatim Service and, second, because their coverage and data quality is almost as good as the service provided by Google Maps.

Having said all this, we can begin with the actual example.

## How to geocode addresses using the OSM Nominatim Service?

The key packages that we are going to be using are two: the `sf` and `tmaptools` R packages. The [sf package](https://r-spatial.github.io/sf/index.html) allow us to access and handle **simple features** using R programming language. If you are not familiar with the concept of simple features, I would suggest you to read [this article](https://r-spatial.github.io/sf/articles/sf1.html) written by Edzer Pebesma. On the other hand, the [tmaptools package](https://github.com/r-tmap/tmaptools) is an R-library that provides a wide set of tools for reading and processing spatial data, including the `geocode_OSM()` function which will allow us to access the OSM Nominatim Service to geocode strings of text.

Both packages can be installed as follows:

    install.packages("sf")
    install_github("mtennekes/tmaptools")

Now that we know the tools, lets take a look at the data. For this, we first need to load the libraries that we are going to be using and, then, we can read and check the data that we have.

``` r
# Loading required libraries
library(tmaptools)
library(sf)
```

    ## Linking to GEOS 3.8.1, GDAL 3.2.1, PROJ 7.2.1

``` r
library(tidyverse)
```

    ## Warning: package 'tidyverse' was built under R version 4.1.2

    ## ── Attaching packages
    ## ───────────────────────────────────────
    ## tidyverse 1.3.2 ──

    ## ✔ ggplot2 3.4.1     ✔ purrr   0.3.4
    ## ✔ tibble  3.1.8     ✔ dplyr   1.0.9
    ## ✔ tidyr   1.2.0     ✔ stringr 1.4.1
    ## ✔ readr   2.1.2     ✔ forcats 0.5.1

    ## Warning: package 'ggplot2' was built under R version 4.1.2

    ## Warning: package 'tibble' was built under R version 4.1.2

    ## Warning: package 'tidyr' was built under R version 4.1.2

    ## Warning: package 'readr' was built under R version 4.1.2

    ## Warning: package 'dplyr' was built under R version 4.1.2

    ## Warning: package 'stringr' was built under R version 4.1.2

    ## ── Conflicts ────────────────────────────────────────── tidyverse_conflicts() ──
    ## ✖ dplyr::filter() masks stats::filter()
    ## ✖ dplyr::lag()    masks stats::lag()

``` r
# Reading data
austria_data.df <- read_csv("Austria_data.csv")
```

    ## Rows: 6925 Columns: 4
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ","
    ## chr (4): address, phone, email, website
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

``` r
# How does data look like?
austria_data.df %>%
  slice_head(n = 15) %>%
  knitr::kable(format = "html")
```

<table>
<thead>
<tr>
<th style="text-align:left;">
address
</th>
<th style="text-align:left;">
phone
</th>
<th style="text-align:left;">
email
</th>
<th style="text-align:left;">
website
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:left;">
1010 Wien–Stubenring 18
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
No
</td>
</tr>
<tr>
<td style="text-align:left;">
5020 Salzburg–Mildenburggasse 1/2
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
No
</td>
</tr>
<tr>
<td style="text-align:left;">
1010 Wien–Stubenring 18
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
</tr>
<tr>
<td style="text-align:left;">
1010 Wien–Stubenring 18
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
No
</td>
</tr>
<tr>
<td style="text-align:left;">
6900 Bregenz–Rathausstraße 37
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
</tr>
<tr>
<td style="text-align:left;">
1010 Wien–Spiegelgasse 19
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
No
</td>
</tr>
<tr>
<td style="text-align:left;">
1220 Wien–ARES Tower, Donau-City-Straße 11
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
</tr>
<tr>
<td style="text-align:left;">
1030 Wien–Riesgasse 3/14
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
No
</td>
</tr>
<tr>
<td style="text-align:left;">
1010 Wien–Wollzeile 17/22
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
</tr>
<tr>
<td style="text-align:left;">
1010 Wien–Wollzeile 17/22
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
</tr>
<tr>
<td style="text-align:left;">
1010 Wien–Kohlmarkt 8-10/Eing. Wallnerstr. 1
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
</tr>
<tr>
<td style="text-align:left;">
1070 Wien–Neustiftgasse 3/7
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
</tr>
<tr>
<td style="text-align:left;">
3100 St. Pölten–Domgasse 2
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
No
</td>
</tr>
<tr>
<td style="text-align:left;">
6020 Innsbruck–Wilhelm-Greil-Straße 21/IV.
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
No
</td>
</tr>
<tr>
<td style="text-align:left;">
6800 Feldkirch–Schloßgraben 10
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
<td style="text-align:left;">
Yes
</td>
</tr>
</tbody>
</table>

As we can observe, we have a data frame with four columns. For now, we will focus exclusively in the first one, the address. All the addresses follow the same pattern: a four digits sequence representing the corresponding ZIP code, followed by the name of the city or town in which the individual is located, followed by a line break represented by two hyphens (–) and then, after this line break, we have the street name and the house number. First, let’s change the line break by a comma and extract only the address information:

``` r
# Replacing line breaks by commas
addresses <- austria_data.df %>%
  mutate(address = str_replace_all(address, "--", ", ")) %>%
  pull(address)

# How do the addresses look like?
addresses[1:15]
```

    ##  [1] "1010 Wien, Stubenring 18"                     
    ##  [2] "5020 Salzburg, Mildenburggasse 1/2"           
    ##  [3] "1010 Wien, Stubenring 18"                     
    ##  [4] "1010 Wien, Stubenring 18"                     
    ##  [5] "6900 Bregenz, Rathausstraße 37"               
    ##  [6] "1010 Wien, Spiegelgasse 19"                   
    ##  [7] "1220 Wien, ARES Tower, Donau-City-Straße 11"  
    ##  [8] "1030 Wien, Riesgasse 3/14"                    
    ##  [9] "1010 Wien, Wollzeile 17/22"                   
    ## [10] "1010 Wien, Wollzeile 17/22"                   
    ## [11] "1010 Wien, Kohlmarkt 8-10/Eing. Wallnerstr. 1"
    ## [12] "1070 Wien, Neustiftgasse 3/7"                 
    ## [13] "3100 St. Pölten, Domgasse 2"                  
    ## [14] "6020 Innsbruck, Wilhelm-Greil-Straße 21/IV."  
    ## [15] "6800 Feldkirch, Schloßgraben 10"

A clean string of text increases the likelihood of capturing the desired location with accuracy. Therefore, it is highly recommended to check for encoding or misspelling issues before passing the string to the geocoding function. Once that you have make sure that you are passing tidy and clean strings, you need to know beforehand certain aspects. For example, in which projection system do you want the coordinates to be?, or, in which data structure do you want the output to be returned?

For this example, I’m gonna be retrieving the coordinates in a longitude-latiutude system. More specifically, in the World Geodetic System or WGS84, which is also refered to as the EPSG 4326 system. An explanation of the different projection systems would required their own post, which escapes from the scope of this one at present. Therefore, if you are not familiar with projection systems, I would highly suggest you to watch the following video:

<iframe width="560" height="315" src="https://www.youtube.com/embed/NAzy4S4EOwc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
</iframe>

After you have decided in which projection system do you want your coordinates to be, `geocode_OSM()` allows you to decide in which data structure you want your data to be returned. For this example, I am asking the output to be returned as a simple feature. Let’s geocode the first 100 addresses that we have in our registry and check how does the information look like.

``` r
# Replacing line breaks by commas
geocoded_addresses <- geocode_OSM(addresses[1:100], 
                                  projection = 4326, 
                                  as.sf      = T)
```

    ## No results found for "1220 Wien, ARES Tower, Donau-City-Straße 11".

    ## No results found for "1010 Wien, Kohlmarkt 8-10/Eing. Wallnerstr. 1".

    ## No results found for "1080 Wien, Mölkergasse 3/7".

    ## No results found for "1010 Wien, Tuchlauben 7a(Eingang Seitzergasse 6)".

    ## No results found for "6020 Innsbruck, Erlerstraße 19 / 3. Stock (Top 34)".

    ## No results found for "1010 Wien, Tuchlauben 11/2/13-14".

    ## No results found for "1010 Wien, Rotenturmstraße 19/II/36".

    ## No results found for "1220 Wien, Lavaterstraße 7/4/24".

    ## No results found for "1060 Wien, Mariahilfer Straße 47/3/5".

    ## No results found for "1010 Wien, Lugeck 1-2/Stiege 2/Top 12".

    ## No results found for "1170 Wien, Ottakringer Straße 54/Top 3.2".

    ## No results found for "1090 Wien, Rooseveltplatz 4-5/8".

    ## No results found for "1010 Wien, An der Hülben 4, Top 7".

    ## No results found for "1010 Wien, Volksgartenstraße 3/2. OG".

    ## No results found for "1010 Wien, Doblhoffgasse 9, Top 14".

    ## No results found for "1030 Wien, Ungargasse 59-61, Top 301".

    ## No results found for "9800 Spittal/Drau, Am Rathausplatz 1/1".

``` r
# How does this new information looks like
geocoded_addresses %>%
  slice_head(n = 15) %>%
  knitr::kable(format = "html")
```

<table>
<thead>
<tr>
<th style="text-align:left;">
query
</th>
<th style="text-align:right;">
x
</th>
<th style="text-align:right;">
y
</th>
<th style="text-align:right;">
y_min
</th>
<th style="text-align:right;">
y_max
</th>
<th style="text-align:right;">
x_min
</th>
<th style="text-align:right;">
x_max
</th>
<th style="text-align:left;">
bbox
</th>
<th style="text-align:left;">
point
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:left;">
1010 Wien, Stubenring 18
</td>
<td style="text-align:right;">
16.381229
</td>
<td style="text-align:right;">
48.20844
</td>
<td style="text-align:right;">
48.20839
</td>
<td style="text-align:right;">
48.20849
</td>
<td style="text-align:right;">
16.381179
</td>
<td style="text-align:right;">
16.381280
</td>
<td style="text-align:left;">
POLYGON ((16.38118 48.20839…
</td>
<td style="text-align:left;">
POINT (16.38123 48.20844)
</td>
</tr>
<tr>
<td style="text-align:left;">
5020 Salzburg, Mildenburggasse 1/2
</td>
<td style="text-align:right;">
13.062617
</td>
<td style="text-align:right;">
47.79873
</td>
<td style="text-align:right;">
47.79873
</td>
<td style="text-align:right;">
47.79881
</td>
<td style="text-align:right;">
13.062602
</td>
<td style="text-align:right;">
13.062617
</td>
<td style="text-align:left;">
POLYGON ((13.0626 47.79873,…
</td>
<td style="text-align:left;">
POINT (13.06262 47.79873)
</td>
</tr>
<tr>
<td style="text-align:left;">
1010 Wien, Stubenring 18
</td>
<td style="text-align:right;">
16.381229
</td>
<td style="text-align:right;">
48.20844
</td>
<td style="text-align:right;">
48.20839
</td>
<td style="text-align:right;">
48.20849
</td>
<td style="text-align:right;">
16.381179
</td>
<td style="text-align:right;">
16.381280
</td>
<td style="text-align:left;">
POLYGON ((16.38118 48.20839…
</td>
<td style="text-align:left;">
POINT (16.38123 48.20844)
</td>
</tr>
<tr>
<td style="text-align:left;">
1010 Wien, Stubenring 18
</td>
<td style="text-align:right;">
16.381229
</td>
<td style="text-align:right;">
48.20844
</td>
<td style="text-align:right;">
48.20839
</td>
<td style="text-align:right;">
48.20849
</td>
<td style="text-align:right;">
16.381179
</td>
<td style="text-align:right;">
16.381280
</td>
<td style="text-align:left;">
POLYGON ((16.38118 48.20839…
</td>
<td style="text-align:left;">
POINT (16.38123 48.20844)
</td>
</tr>
<tr>
<td style="text-align:left;">
6900 Bregenz, Rathausstraße 37
</td>
<td style="text-align:right;">
9.746105
</td>
<td style="text-align:right;">
47.50451
</td>
<td style="text-align:right;">
47.50442
</td>
<td style="text-align:right;">
47.50459
</td>
<td style="text-align:right;">
9.745983
</td>
<td style="text-align:right;">
9.746226
</td>
<td style="text-align:left;">
POLYGON ((9.745983 47.50442…
</td>
<td style="text-align:left;">
POINT (9.746105 47.5045)
</td>
</tr>
<tr>
<td style="text-align:left;">
1010 Wien, Spiegelgasse 19
</td>
<td style="text-align:right;">
16.369606
</td>
<td style="text-align:right;">
48.20635
</td>
<td style="text-align:right;">
48.20621
</td>
<td style="text-align:right;">
48.20649
</td>
<td style="text-align:right;">
16.369477
</td>
<td style="text-align:right;">
16.369900
</td>
<td style="text-align:left;">
POLYGON ((16.36948 48.20621…
</td>
<td style="text-align:left;">
POINT (16.36961 48.20635)
</td>
</tr>
<tr>
<td style="text-align:left;">
1030 Wien, Riesgasse 3/14
</td>
<td style="text-align:right;">
16.389144
</td>
<td style="text-align:right;">
48.19857
</td>
<td style="text-align:right;">
48.19813
</td>
<td style="text-align:right;">
48.19908
</td>
<td style="text-align:right;">
16.389128
</td>
<td style="text-align:right;">
16.389157
</td>
<td style="text-align:left;">
POLYGON ((16.38913 48.19813…
</td>
<td style="text-align:left;">
POINT (16.38914 48.19857)
</td>
</tr>
<tr>
<td style="text-align:left;">
1010 Wien, Wollzeile 17/22
</td>
<td style="text-align:right;">
16.376252
</td>
<td style="text-align:right;">
48.20840
</td>
<td style="text-align:right;">
48.20765
</td>
<td style="text-align:right;">
48.20965
</td>
<td style="text-align:right;">
16.373491
</td>
<td style="text-align:right;">
16.378753
</td>
<td style="text-align:left;">
POLYGON ((16.37349 48.20765…
</td>
<td style="text-align:left;">
POINT (16.37625 48.2084)
</td>
</tr>
<tr>
<td style="text-align:left;">
1010 Wien, Wollzeile 17/22
</td>
<td style="text-align:right;">
16.376252
</td>
<td style="text-align:right;">
48.20840
</td>
<td style="text-align:right;">
48.20765
</td>
<td style="text-align:right;">
48.20965
</td>
<td style="text-align:right;">
16.373491
</td>
<td style="text-align:right;">
16.378753
</td>
<td style="text-align:left;">
POLYGON ((16.37349 48.20765…
</td>
<td style="text-align:left;">
POINT (16.37625 48.2084)
</td>
</tr>
<tr>
<td style="text-align:left;">
1070 Wien, Neustiftgasse 3/7
</td>
<td style="text-align:right;">
16.337271
</td>
<td style="text-align:right;">
48.20616
</td>
<td style="text-align:right;">
48.20615
</td>
<td style="text-align:right;">
48.20616
</td>
<td style="text-align:right;">
16.337165
</td>
<td style="text-align:right;">
16.337400
</td>
<td style="text-align:left;">
POLYGON ((16.33717 48.20615…
</td>
<td style="text-align:left;">
POINT (16.33727 48.20616)
</td>
</tr>
<tr>
<td style="text-align:left;">
3100 St. Pölten, Domgasse 2
</td>
<td style="text-align:right;">
15.624754
</td>
<td style="text-align:right;">
48.20537
</td>
<td style="text-align:right;">
48.20532
</td>
<td style="text-align:right;">
48.20542
</td>
<td style="text-align:right;">
15.624704
</td>
<td style="text-align:right;">
15.624804
</td>
<td style="text-align:left;">
POLYGON ((15.6247 48.20532,…
</td>
<td style="text-align:left;">
POINT (15.62475 48.20537)
</td>
</tr>
<tr>
<td style="text-align:left;">
6020 Innsbruck, Wilhelm-Greil-Straße 21/IV.
</td>
<td style="text-align:right;">
11.397080
</td>
<td style="text-align:right;">
47.26507
</td>
<td style="text-align:right;">
47.26507
</td>
<td style="text-align:right;">
47.26518
</td>
<td style="text-align:right;">
11.397080
</td>
<td style="text-align:right;">
11.397115
</td>
<td style="text-align:left;">
POLYGON ((11.39708 47.26507…
</td>
<td style="text-align:left;">
POINT (11.39708 47.26507)
</td>
</tr>
<tr>
<td style="text-align:left;">
6800 Feldkirch, Schloßgraben 10
</td>
<td style="text-align:right;">
9.599081
</td>
<td style="text-align:right;">
47.23846
</td>
<td style="text-align:right;">
47.23841
</td>
<td style="text-align:right;">
47.23851
</td>
<td style="text-align:right;">
9.599031
</td>
<td style="text-align:right;">
9.599131
</td>
<td style="text-align:left;">
POLYGON ((9.599031 47.23841…
</td>
<td style="text-align:left;">
POINT (9.599081 47.23846)
</td>
</tr>
<tr>
<td style="text-align:left;">
4020 Linz, Schillerstraße 12
</td>
<td style="text-align:right;">
14.293445
</td>
<td style="text-align:right;">
48.29761
</td>
<td style="text-align:right;">
48.29756
</td>
<td style="text-align:right;">
48.29766
</td>
<td style="text-align:right;">
14.293395
</td>
<td style="text-align:right;">
14.293495
</td>
<td style="text-align:left;">
POLYGON ((14.2934 48.29756,…
</td>
<td style="text-align:left;">
POINT (14.29345 48.29761)
</td>
</tr>
<tr>
<td style="text-align:left;">
5020 Salzburg, Erzabt-Klotz-Straße 12/2
</td>
<td style="text-align:right;">
13.052071
</td>
<td style="text-align:right;">
47.79254
</td>
<td style="text-align:right;">
47.79251
</td>
<td style="text-align:right;">
47.79254
</td>
<td style="text-align:right;">
13.051968
</td>
<td style="text-align:right;">
13.052071
</td>
<td style="text-align:left;">
POLYGON ((13.05197 47.79251…
</td>
<td style="text-align:left;">
POINT (13.05207 47.79254)
</td>
</tr>
</tbody>
</table>

## Visualizing the results

The output we receive has information regarding the longitude, latitudes and bounding box of the simple feature we submitted. Let’s try to visualize these geographical coordinates in a map using the [Leaflet package](https://rstudio.github.io/leaflet/) (*Remember that you can zoom in a certain area of the map to see the spread of individuals in detail*):

``` r
library(leaflet)
```

    ## Warning: package 'leaflet' was built under R version 4.1.2

``` r
leaflet() %>% 
      addProviderTiles(providers$CartoDB.Voyager) %>%
      setView(lng  = 13.5306, 
              lat  = 47.4968, 
              zoom = 7) %>%
      addMarkers(
        data         = geocoded_addresses,
        lng          = ~x,
        lat          = ~y,
        popup        = ~query
      )
```

<div id="htmlwidget-1" style="width:672px;height:480px;" class="leaflet html-widget"></div>
<script type="application/json" data-for="htmlwidget-1">{"x":{"options":{"crs":{"crsClass":"L.CRS.EPSG3857","code":null,"proj4def":null,"projectedBounds":null,"options":{}}},"calls":[{"method":"addProviderTiles","args":["CartoDB.Voyager",null,null,{"errorTileUrl":"","noWrap":false,"detectRetina":false}]},{"method":"addMarkers","args":[[48.2084372,47.7987302,48.2084372,48.2084372,47.504505,48.20635465,48.198573,48.2084025,48.2084025,48.2061592,48.20537,47.2650689,47.2384644,48.2976086,47.792545,48.1997712,48.2119602,48.2146503,48.2058152,48.2456639,48.2054655,48.2158025,48.2071736,48.30210145,48.221665,46.6263052,48.2158025,47.8096497,47.8105416,47.91794995,48.0034127,47.2639369,48.2028819,48.29336915,47.2629762,48.2474234,48.0679848,48.21689875,48.21689875,48.1588177,48.2109795,48.2018829,48.21021685,47.2366996,48.194618,48.2071736,48.2162524,48.2070967,48.30745715,48.2120958,48.211328,48.2146025,48.1979256,48.2151505,48.0843371,48.3299838,48.2092099,47.8140757,48.2070407,48.1990893,47.2652479,48.18553525,48.2061592,48.2015129,48.2123435,48.305432,48.2158025,47.2736434,48.2154968,48.1942116,48.211876,48.2072168,47.2706546,47.2657138,48.20635465,48.212928,48.2028819,48.2320736,48.1527985,48.2121834,48.2337285,48.2082704,48.2075477],[16.3812295,13.0626175,16.3812295,16.3812295,9.74610478388846,16.3696062602824,16.3891437,16.3762524,16.3762524,16.3372714,15.6247537,11.3970805,9.5990814,14.293445,13.0520711,16.3769655,16.3685648,16.3647241,16.372196,16.3426193,16.3781489,16.3673736,16.3799658,14.2776218451953,14.2382707,14.3097983,16.3673736,13.0580355,13.0472921,13.8081628485638,13.9223305,11.4094936,16.3755581,14.2902162,11.3948968,14.2347503,13.4925199677375,16.382044934737,16.382044934737,14.0205284484472,16.3716207,16.3450036,13.9048641563107,9.59468467222494,16.3503197,16.3799658,16.3675083,16.3882044,16.3202341449967,16.3721048,16.3914645,16.3691793,16.3673041,16.3578866,16.2863552,16.212649,16.371048,16.2404567905134,16.3724007,16.3751712,11.3917298,16.299154347965,16.3372714,16.3720471,16.4121517,14.2862217,16.3673736,9.63878300375598,16.3652433,16.353952,16.3486552,16.3683934,15.3257302,11.3974397,16.3696062602824,16.3617954,16.3755581,16.3267629,14.0087014797429,16.3639417,13.8300819,16.3802593,16.3681177],null,null,null,{"interactive":true,"draggable":false,"keyboard":true,"title":"","alt":"","zIndexOffset":0,"opacity":1,"riseOnHover":false,"riseOffset":250},["1010 Wien, Stubenring 18","5020 Salzburg, Mildenburggasse 1/2","1010 Wien, Stubenring 18","1010 Wien, Stubenring 18","6900 Bregenz, Rathausstraße 37","1010 Wien, Spiegelgasse 19","1030 Wien, Riesgasse 3/14","1010 Wien, Wollzeile 17/22","1010 Wien, Wollzeile 17/22","1070 Wien, Neustiftgasse 3/7","3100 St. Pölten, Domgasse 2","6020 Innsbruck, Wilhelm-Greil-Straße 21/IV.","6800 Feldkirch, Schloßgraben 10","4020 Linz, Schillerstraße 12","5020 Salzburg, Erzabt-Klotz-Straße 12/2","1030 Wien, Am Heumarkt 10","1010 Wien, Färbergasse 10/15","1010 Wien, Schottenring 12","1010 Wien, Himmelpfortgasse 20/2","1190 Wien, Billrothstraße 86/2","1010 Wien, Parkring 12","1010 Wien, Schottenring 19","1010 Wien, Parkring 2","4020 Linz, Lessingstraße 40","4050 Traun, Neubauerstraße 14/1","9020 Klagenfurt, Waaggasse 18/2","1010 Wien, Schottenring 19","5020 Salzburg, Sterneckstraße 35","5020 Salzburg, Paracelsusstraße 27","4810 Gmunden, Schlagenstraße 17","4655 Vorchdorf, Schloßplatz 15","6020 Innsbruck, Gumppstraße 53-55","1010 Wien, Schubertring 6","4020 Linz, Weingartshofstraße 21","6020 Innsbruck, Maria-Theresien-Straße 57","4061 Pasching, Kramlehnerweg 1a","4873 Frankenburg, Marktplatz 1","1020 Wien, Taborstraße 24a","1020 Wien, Taborstraße 24a","4600 Wels, Dr.-Koss-Straße 2","1010 Wien, Tuchlauben 11/18","1070 Wien, Zieglergasse 39/15","4632 Pichl bei Wels, Fadleiten 18","6800 Feldkirch, Vorstadt 18","1060 Wien, Otto-Bauer-Gasse 4/5","1010 Wien, Parkring 2","1010 Wien, Schottenring 35/6a","1030 Wien, Marxergasse 5/24","3400 Klosterneuburg, Kierlinger Straße 12","1010 Wien, Sterngasse 13","1030 Wien, Untere Viaduktgasse 10/12","1010 Wien, Werdertorgasse 15/16","1040 Wien, Rilkeplatz 8","1090 Wien, Rooseveltplatz 4-5","2340 Mödling, Babenbergergasse 1/1","3423 St. Andrä-Wördern, Josef Karnerplatz 1","1010 Wien, Bauernmarkt 2","2700 Wiener Neustadt, Herrengasse 25","1010 Wien, Weihburggasse 20/33","1040 Wien, Brucknerstraße 4/5","6020 Innsbruck, Fallmerayerstraße 8/DG","1130 Wien, Altgasse 16","1070 Wien, Neustiftgasse 3/7","1010 Wien, Kärntner Ring 12","1020 Wien, Trabrennstraße 2B","4020 Linz, Hauptplatz 17","1010 Wien, Schottenring 19","6830 Rankweil, Kreuzlinger Straße 14","1010 Wien, Wipplingerstraße 20/8-9","1060 Wien, Linke Wienzeile 4/2/6","1080 Wien, Lederergasse 16/3","1010 Wien, Stallburggasse 4/6","8130 Frohnleiten, Hauptplatz 2","6020 Innsbruck, Wilhelm-Greil-Straße 9","1010 Wien, Spiegelgasse 19","1010 Wien, Universitätsring 10","1010 Wien, Schubertring 6","1180 Wien, Wallrißstraße 72/1","4600 Wels, Edisonstraße 1/WDZ 8","1010 Wien, Schottengasse 1","4710 Grieskirchen, Uferstraße 4","1010 Wien, Biberstraße 5","1010 Wien, Stallburggasse 4"],null,null,null,null,{"interactive":false,"permanent":false,"direction":"auto","opacity":1,"offset":[0,0],"textsize":"10px","textOnly":false,"className":"","sticky":true},null]}],"setView":[[47.4968,13.5306],7,[]],"limits":{"lat":[46.6263052,48.3299838],"lng":[9.59468467222494,16.4121517]}},"evals":[],"jsHooks":[]}</script>

By geocoding the full addresses we get a very accurate point. Hoever, it’s possible that we would prefer to group locations that are close to each other and see the major concentrations of lawyers in the country. For this, we can group individuals by major locations such as cities or towns. For this, we can extract information from the address. Remember that, following the ZIP code, we have the name of the location in which the individual resides. We can use this demographic level to group individuals. Let’s extract this information using regular expressions:

``` r
# Grouping individuals and extracting the information
grouped_data.df <- austria_data.df %>%
  mutate(location = str_extract(address, "(?<=\\d{4}\\s).+(?=--)"),
         location = paste0(location, ", Austria")) %>%
  group_by(location) %>%
  summarise(total = n()) %>%
  arrange(desc(total))

# How do the data look like?
grouped_data.df %>%
  slice_head(n = 15) %>%
  knitr::kable(format = "html")
```

<table>
<thead>
<tr>
<th style="text-align:left;">
location
</th>
<th style="text-align:right;">
total
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:left;">
Wien, Austria
</td>
<td style="text-align:right;">
3563
</td>
</tr>
<tr>
<td style="text-align:left;">
Graz, Austria
</td>
<td style="text-align:right;">
379
</td>
</tr>
<tr>
<td style="text-align:left;">
Innsbruck, Austria
</td>
<td style="text-align:right;">
342
</td>
</tr>
<tr>
<td style="text-align:left;">
Salzburg, Austria
</td>
<td style="text-align:right;">
333
</td>
</tr>
<tr>
<td style="text-align:left;">
Linz, Austria
</td>
<td style="text-align:right;">
315
</td>
</tr>
<tr>
<td style="text-align:left;">
Klagenfurt, Austria
</td>
<td style="text-align:right;">
133
</td>
</tr>
<tr>
<td style="text-align:left;">
Wels, Austria
</td>
<td style="text-align:right;">
88
</td>
</tr>
<tr>
<td style="text-align:left;">
Dornbirn, Austria
</td>
<td style="text-align:right;">
67
</td>
</tr>
<tr>
<td style="text-align:left;">
St. Pölten, Austria
</td>
<td style="text-align:right;">
63
</td>
</tr>
<tr>
<td style="text-align:left;">
Bregenz, Austria
</td>
<td style="text-align:right;">
53
</td>
</tr>
<tr>
<td style="text-align:left;">
Feldkirch, Austria
</td>
<td style="text-align:right;">
53
</td>
</tr>
<tr>
<td style="text-align:left;">
Wiener Neustadt, Austria
</td>
<td style="text-align:right;">
53
</td>
</tr>
<tr>
<td style="text-align:left;">
Villach, Austria
</td>
<td style="text-align:right;">
49
</td>
</tr>
<tr>
<td style="text-align:left;">
Mödling, Austria
</td>
<td style="text-align:right;">
46
</td>
</tr>
<tr>
<td style="text-align:left;">
Baden, Austria
</td>
<td style="text-align:right;">
34
</td>
</tr>
</tbody>
</table>

As a result of the grouping, we have a data frame containing the names of 370 locations scattered all over Austria and sorted by the number of lawyers residing in that city or town. We can grab this list of locations and geocode them in order to retrieve their geographical coordinates as follows:

``` r
# Replacing line breaks by commas
geocoded_addresses <- geocode_OSM(grouped_data.df %>% pull(location), 
                                  projection = 4326, 
                                  as.sf      = T)
```

    ## No results found for "St. Jakob i. H., Austria".

    ## No results found for "Hochrum bei Innsbruck, Austria".

    ## No results found for "Kirchbach i.d. Stmk., Austria".

    ## No results found for "Neumarkt/Stmk, Austria".

``` r
# Joining total number of lawyers to geocoded data
geocoded_addresses <- geocoded_addresses %>%
  select(location = query, x, y) %>%
  left_join(grouped_data.df,
            by = "location") %>%
  mutate(label4map = paste("<p><strong>", location, "</strong><br/>",
                           "Number of lawyers: ", total, "</p>"))
```

Let’s visualize this data into a Leaflet map and identify the major demographic concentrations of lawyers (*Remember than you can scroll over a marker to see the location and the number of lawyers in that city or town*):

``` r
leaflet() %>% 
      addProviderTiles(providers$CartoDB.Voyager) %>%
      setView(lng  = 13.5306, 
              lat  = 47.4968, 
              zoom = 7) %>%
  addCircleMarkers(data         = geocoded_addresses,
                   lng          = ~x,
                   lat          = ~y,
                   radius       = ~(total)^(1/3.5),
                   color        = "#00A08A",
                   fillOpacity  = 0.1,
                   label        = lapply(geocoded_addresses$label4map, shiny::HTML),
                   labelOptions = labelOptions(style = list("font-weight" = "normal", 
                                                            padding = "3px 8px", 
                                                            "color" = "#00A08A"),
                                               textsize  = "15px", 
                                               direction = "auto")
      )
```

<div id="htmlwidget-2" style="width:672px;height:480px;" class="leaflet html-widget"></div>
<script type="application/json" data-for="htmlwidget-2">{"x":{"options":{"crs":{"crsClass":"L.CRS.EPSG3857","code":null,"proj4def":null,"projectedBounds":null,"options":{}}},"calls":[{"method":"addProviderTiles","args":["CartoDB.Voyager",null,null,{"errorTileUrl":"","noWrap":false,"detectRetina":false}]},{"method":"addCircleMarkers","args":[[48.2083537,47.0708678,47.2654296,47.7981346,48.3059078,46.623943,48.1565472,47.413631,48.2043985,47.5025779,47.2375671,47.80708635,46.6167284,48.0855922,48.0085749,47.582996,47.4463585,48.0390046,47.83875775,48.2085868,48.4108382,47.153037,48.3440605,47.3805128,47.9185855,46.7804762,46.623943,47.48033265,48.0999102,48.0078587,47.4057201,47.2759021,47.1274736,46.7905474,46.8146272,47.6821521,47.7221147,48.4643006,47.3449529,47.3046511,48.3311686,47.2816648,47.2861513,46.7389586,47.3239636,48.253136,47.3351291,48.235011,46.82958615,48.1169363,47.3940415,48.3082607,48.5112961,47.0499925,48.3403867,47.106751,48.6636596,48.1030792,47.416719,48.2214369,46.8390583,48.0255094,47.2809371,48.30499,47.80074505,47.504516,47.7115299,47.4168029,47.489391,48.0919647,47.5070965,48.2272068,48.5694535,48.10499675,48.3846124,48.8147061,48.2141482,46.7284183,48.2843295,48.54886325,47.0644882,48.2793314,47.8560014,47.4981426,46.6604246,48.250022,47.9016069,46.9525777,47.3469156,48.7859752,47.0038493,47.1694082,48.2651355,47.2147399,47.4276538,47.7368423,47.36123525,48.2085868,47.99771495,47.0691666,47.3783583,48.16847735,47.2174206,48.602082,48.015706,47.6094985,47.1703104,47.8671332,48.11013505,47.4405481,47.905194,47.9744729,46.914433,47.11958265,48.1971022,48.2500898,46.96298025,47.2731056,47.44782555,48.2012891,46.6196646,47.0504742,48.0035141,48.2303903,47.9455876,47.8122366,47.7592351,48.1334587,47.05552765,46.6538822,47.3639973,48.0533652,47.5294182,48.1907992,48.2404063,47.1672188,47.2815157,47.6053538,47.6171008,48.2119885,48.2076724,47.3846705,48.75053735,47.4218385,48.0545249,48.2741408,47.8942481,47.1261065,47.9512695,47.7218417,48.1772445,48.3729785,47.7497338,47.6408949,47.50894245,47.9655519,47.36458585,46.5911257,48.1070931,47.96611095,46.6860661,46.9360244,46.5265324,47.19001725,46.9520636,47.2715315,46.8742452,46.9969426,47.1231264,47.1295033,47.4459809,48.1849148,48.0450052,47.0443248,47.5043706,46.9371733,46.7921853,47.51380975,47.4553157,46.6257965,47.46047585,48.7125893,47.9825598,48.3096359,46.9749381,47.9880551,47.2176683,48.3438653,48.1792064,47.1974668,48.5723052,47.2922308,47.524226,48.2181486,47.3208816,47.2264001,48.2012891,47.9802351,47.2876898,48.0885947,48.1298877,48.105069,48.38189735,47.22648565,47.22648565,48.5447465,47.2965003,47.5276244,46.871383,48.1534694,48.2207703,47.1144954,48.0348017,46.8144214,46.6880556,47.0696267,47.8408541,47.1525608,48.1979315,47.2866946,48.0198451,48.1070931,47.3856495,47.1990318,48.9160904,46.7790056,47.13725755,47.4314481,48.0765942,47.8571336,47.414646,48.175888,48.0882154,48.0680308,47.9855432,47.837745,47.1530974,48.2351521,48.3531392,47.85589855,48.5951053,48.0222203,48.1992201,47.3300683,47.24176735,47.5908563,48.2271779,47.7401445,48.5731094,48.04717635,48.2051627,48.1466103,46.9918461,46.9553629,47.8994623,48.0801855,47.0203661,47.4598203,47.4500151,47.4667493,48.1928265,46.9218,47.7610752,47.2135194,47.94932765,46.95820285,47.2713898,47.2542856,47.5049711,48.41023695,48.320852,47.22916085,47.4747262,46.8522,47.9733296,47.9285336,47.3702802,47.193859,47.0546863,47,48.2533971,48.1889436,47.3412076,47.4366555,46.7083655,47.5142934,47.1720767,48.4842345,48.1379716,48.273967,47.917685,48.0455687,46.7547877,47.1717622,47.9380101,47.9611479,48.3318812,48.2576453,48.3545278,47.9614255,47.8881417,48.0173229,47.4570287,48.1851073,47.2270975,47.9969423,46.6359543,47.78490215,48.3549856,47.02233175,47.1582215,47.991944,46.6529844,47.4663998,48.1801065,47.0006028,47.0512948,47.0492181,47.2867829,47.904491,47.2059776,46.8190736,47.3289241,47.0047875,47.0122176,48.0138872,48.0378279,47.8105684,47.1049888,47.5104298,48.31739315,47.7670412,48.2932421,47.2991535,47.1277657,46.738948,48.0838623,46.8936066,47.0455874,47.1377347,47.1592565,47.0982303,48.2854468,47.52569825,47.7066007,47.8414905,48.1522388,48.1522388,47.2205845,48.01657665,47.8448255,47.4251065,47.3143054,47.2861267,47.2523245,47.5948303,47.2935786,47.9497066,47.1569227,47.4757761,47.4615532,47.3831879,46.8873498,48.3275396,47.1912045,47.2733773],[16.3725042,15.4382786,11.3927685,13.0464806,14.286198,14.3075976,14.0243752,9.7423875,15.6229118,9.7472924,9.5981724,16.2332604795382,13.8500268,16.2833526,16.2334951,12.1692134,12.3911473,14.4191276,16.5362158649556,13.48839,15.6003717,9.8219314,16.3334321,15.0947756,13.8003048,15.5407005,14.3075976,12.0792806766896,14.8259206046318,13.6460378,15.2498137,10.700690365219,10.5556802234923,13.4872101,15.2137799,13.0956313,16.081602,13.4345986,11.7084253,11.071515,16.0567744,11.5075337,16.2124214,14.385421,12.7963165,13.039506,9.6440092,13.826192,12.7503162096291,16.2559683801349,13.6867878,14.0203999,14.5047566,16.0816815,16.7187051,15.710006557613,15.6563147,13.1503106,12.84778,14.2368078,14.8452061,16.7790041,15.9691769,16.323756,16.7368504672055,16.4944302599851,13.6239333,13.2170933,9.6916539,13.8724131,14.212568375549,15.3369992,16.5720327,16.5848987032657,16.2076303,15.2762681,14.4793948,14.0906473,15.6946065,16.0718969561751,15.0850032,14.2487457,13.3500658,12.4201560952839,14.6340505,13.2320404,13.7652213,15.8887826,11.8527733017511,15.0467102256371,15.4078054,14.6601079,14.1591033457642,14.8297233,9.6599406,16.3980488,10.5456804461982,13.48839,15.1604113753399,9.95288241283492,13.4233713,14.5496245265567,15.6221694,14.9851629,15.9917879,13.7835784,13.1060635,13.1231841,14.5809850227211,15.2901669,14.1244169,16.6038027,14.4266404,14.2255045593288,15.9062673647912,14.6338102,15.4122524134854,9.63150938085392,11.9018281892664,14.378668103282,14.0584346,15.1474771,13.922837,13.9194253,16.1093585,13.7741666,13.0825458,13.9427447,16.32271786462,13.100220072521,9.689271,14.128766,9.7533944,14.1117625,14.5162667,11.8638664,12.4837012,15.6723805,12.2114387,15.2120099,16.1772068,13.4627822,15.9711245161989,9.7313777,13.7749232,14.5817826,13.1260778,13.8103817,14.7445188231802,14.3289935,15.0852856,13.5783677,13.0638706,13.61648,12.123366322345,16.2148073,10.0345727641456,14.8120383819363,16.2836918,16.3916321512555,15.2435062,16.0104808,14.3006203,9.60049781809363,14.4052266,15.3260206,15.826349,15.4869681,15.3304611,15.3189614,13.9008766,16.6006228104622,15.7978459118205,15.517544,14.1042098,16.1412906,15.5385761,12.0911035201581,11.8730433088862,14.2145188,11.9968601375494,16.3745565,13.8225156,16.3572556,15.33376,15.5294814161191,10.6899538038858,13.7710445,16.077089,11.8914901272378,13.9908156,9.6534863,14.3585643,13.8721178,13.1511239,11.0096036973489,14.378668103282,13.2548599,9.6527997,16.3184487235461,15.1376585,15.605799,16.5052472979031,11.8819197326445,11.8819197326445,16.7621379,11.5051409,11.7056026,14.4698793,15.91884,14.421338,13.1352653,14.2091385,13.7983599,15.9880546,15.1267538,13.0221612,9.8123754,15.7624204,12.8241307,16.7792466,16.2836918,11.7971832,15.335976,15.3192244,13.6575527,13.2900775844847,9.8973803,12.9910444,16.3216005,10.9316183461052,15.9928073,13.9470248,13.4921448,13.4191655,16.9241358,11.3490587,16.1284586466602,14.4164196,15.1484170735279,15.6594592,14.4077971,15.5538268,14.4984233,9.63284092276765,13.172292,14.8551948,13.0394938,14.9570948,16.3201963412615,14.2530078,16.9422459,15.5378927721801,15.5854661,13.1882214,16.2390429098669,14.957887,9.6379578,9.8306206,10.6629707656963,13.5431306,12.5208519,16.8008294,11.4336592,16.7890701621713,15.4763586385007,12.7573679,11.2729463,15.4498601,15.8854850300243,16.3124476,11.4316885630877,9.7313331,15.5383,13.6049039,16.216666,11.1424534,9.79546976341689,15.8431863,12.5333333,16.1634120417495,13.1346491,10.9656344116664,11.8134682480276,15.7690617,16.5678493,16.1221437,13.9997079,14.2284929,13.7266998,16.8291317779467,14.335169,13.6074749,9.8003634,13.0752378,13.7927962,14.1757273,14.2044214,15.6183234,14.0161792,14.7171067,16.2644673,13.205675,13.9007289,14.5782189168596,13.3696421,14.1448209,16.3482141999634,14.5308123,15.5087951498638,12.956604,13.688056,14.7110535,12.5600452,16.0242089,15.9346832,15.1246598,16.1224748,11.4573834,13.9609752,9.69704340050001,13.5186548,11.1867187,15.3941982417699,15.3995619,14.6595548554363,16.1757785,12.9854864,15.8269858,12.2064049040586,16.2175963419235,13.3642943,13.4386654,16.238689,16.2696536,13.6331686,13.8694007,15.264379,15.2177953,15.4195952,16.1682822,11.4661524,14.3718463,16.4809395883471,16.0194688,13.2535481,14.030993,14.030993,9.77499178394112,16.3153393606253,13.7902844,15.0065515,11.8529560707177,11.567215,11.3279408,12.1180112,11.5907326,16.4075716,14.7334934,13.1888872,13.2567806,12.2217485594304,15.5145485,16.1762909,14.7549244,11.2422348],[10.346763459718,5.4544888710977,5.29672540775334,5.2565203785323,5.1737211224887,4.04403359326389,3.59390404683435,3.32457134964554,3.26661009489446,3.10921137902068,3.10921137902068,3.10921137902068,3.0402770818287,2.98588905047407,2.7388320720753,2.7388320720753,2.66749332348979,2.64261955393006,2.53675251384931,2.47939698673123,2.44943035721995,2.38658519043364,2.35354689365025,2.35354689365025,2.2837538219638,2.2837538219638,2.24676078289103,2.24676078289103,2.20817902734762,2.16783425256596,2.08098777655185,2.08098777655185,2.08098777655185,2.08098777655185,2.03393700979443,2.03393700979443,2.03393700979443,2.03393700979443,2.03393700979443,2.03393700979443,2.03393700979443,1.98399588562984,1.98399588562984,1.98399588562984,1.98399588562984,1.93069772888325,1.93069772888325,1.93069772888325,1.93069772888325,1.93069772888325,1.93069772888325,1.87344400457448,1.87344400457448,1.87344400457448,1.87344400457448,1.87344400457448,1.87344400457448,1.87344400457448,1.87344400457448,1.87344400457448,1.87344400457448,1.81144732852781,1.81144732852781,1.81144732852781,1.81144732852781,1.81144732852781,1.74363903426962,1.74363903426962,1.74363903426962,1.74363903426962,1.74363903426962,1.74363903426962,1.74363903426962,1.74363903426962,1.74363903426962,1.74363903426962,1.66851044102683,1.66851044102683,1.66851044102683,1.66851044102683,1.66851044102683,1.66851044102683,1.66851044102683,1.66851044102683,1.66851044102683,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.58381960876658,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.48599428913695,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.3687381066422,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1.21901365420448,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],null,null,{"interactive":true,"className":"","stroke":true,"color":"#00A08A","weight":5,"opacity":0.5,"fill":true,"fillColor":"#00A08A","fillOpacity":0.1},null,null,null,null,["<p><strong> Wien, Austria <\/strong><br/> Number of lawyers:  3563 <\/p>","<p><strong> Graz, Austria <\/strong><br/> Number of lawyers:  379 <\/p>","<p><strong> Innsbruck, Austria <\/strong><br/> Number of lawyers:  342 <\/p>","<p><strong> Salzburg, Austria <\/strong><br/> Number of lawyers:  333 <\/p>","<p><strong> Linz, Austria <\/strong><br/> Number of lawyers:  315 <\/p>","<p><strong> Klagenfurt, Austria <\/strong><br/> Number of lawyers:  133 <\/p>","<p><strong> Wels, Austria <\/strong><br/> Number of lawyers:  88 <\/p>","<p><strong> Dornbirn, Austria <\/strong><br/> Number of lawyers:  67 <\/p>","<p><strong> St. Pölten, Austria <\/strong><br/> Number of lawyers:  63 <\/p>","<p><strong> Bregenz, Austria <\/strong><br/> Number of lawyers:  53 <\/p>","<p><strong> Feldkirch, Austria <\/strong><br/> Number of lawyers:  53 <\/p>","<p><strong> Wiener Neustadt, Austria <\/strong><br/> Number of lawyers:  53 <\/p>","<p><strong> Villach, Austria <\/strong><br/> Number of lawyers:  49 <\/p>","<p><strong> Mödling, Austria <\/strong><br/> Number of lawyers:  46 <\/p>","<p><strong> Baden, Austria <\/strong><br/> Number of lawyers:  34 <\/p>","<p><strong> Kufstein, Austria <\/strong><br/> Number of lawyers:  34 <\/p>","<p><strong> Kitzbühel, Austria <\/strong><br/> Number of lawyers:  31 <\/p>","<p><strong> Steyr, Austria <\/strong><br/> Number of lawyers:  30 <\/p>","<p><strong> Eisenstadt, Austria <\/strong><br/> Number of lawyers:  26 <\/p>","<p><strong> Ried/Innkreis, Austria <\/strong><br/> Number of lawyers:  24 <\/p>","<p><strong> Krems, Austria <\/strong><br/> Number of lawyers:  23 <\/p>","<p><strong> Bludenz, Austria <\/strong><br/> Number of lawyers:  21 <\/p>","<p><strong> Korneuburg, Austria <\/strong><br/> Number of lawyers:  20 <\/p>","<p><strong> Leoben, Austria <\/strong><br/> Number of lawyers:  20 <\/p>","<p><strong> Gmunden, Austria <\/strong><br/> Number of lawyers:  18 <\/p>","<p><strong> Leibnitz, Austria <\/strong><br/> Number of lawyers:  18 <\/p>","<p><strong> Klagenfurt am Wörthersee, Austria <\/strong><br/> Number of lawyers:  17 <\/p>","<p><strong> Wörgl, Austria <\/strong><br/> Number of lawyers:  17 <\/p>","<p><strong> Amstetten, Austria <\/strong><br/> Number of lawyers:  16 <\/p>","<p><strong> Vöcklabruck, Austria <\/strong><br/> Number of lawyers:  15 <\/p>","<p><strong> Bruck/Mur, Austria <\/strong><br/> Number of lawyers:  13 <\/p>","<p><strong> Imst, Austria <\/strong><br/> Number of lawyers:  13 <\/p>","<p><strong> Landeck, Austria <\/strong><br/> Number of lawyers:  13 <\/p>","<p><strong> Spittal/Drau, Austria <\/strong><br/> Number of lawyers:  13 <\/p>","<p><strong> Deutschlandsberg, Austria <\/strong><br/> Number of lawyers:  12 <\/p>","<p><strong> Hallein, Austria <\/strong><br/> Number of lawyers:  12 <\/p>","<p><strong> Neunkirchen, Austria <\/strong><br/> Number of lawyers:  12 <\/p>","<p><strong> Schärding/Inn, Austria <\/strong><br/> Number of lawyers:  12 <\/p>","<p><strong> Schwaz, Austria <\/strong><br/> Number of lawyers:  12 <\/p>","<p><strong> Telfs, Austria <\/strong><br/> Number of lawyers:  12 <\/p>","<p><strong> Tulln, Austria <\/strong><br/> Number of lawyers:  12 <\/p>","<p><strong> Hall/Tirol, Austria <\/strong><br/> Number of lawyers:  11 <\/p>","<p><strong> Oberwart, Austria <\/strong><br/> Number of lawyers:  11 <\/p>","<p><strong> St. Veit/Glan, Austria <\/strong><br/> Number of lawyers:  11 <\/p>","<p><strong> Zell/See, Austria <\/strong><br/> Number of lawyers:  11 <\/p>","<p><strong> Braunau/Inn, Austria <\/strong><br/> Number of lawyers:  10 <\/p>","<p><strong> Götzis, Austria <\/strong><br/> Number of lawyers:  10 <\/p>","<p><strong> Grieskirchen, Austria <\/strong><br/> Number of lawyers:  10 <\/p>","<p><strong> Lienz, Austria <\/strong><br/> Number of lawyers:  10 <\/p>","<p><strong> Perchtoldsdorf, Austria <\/strong><br/> Number of lawyers:  10 <\/p>","<p><strong> Schladming, Austria <\/strong><br/> Number of lawyers:  10 <\/p>","<p><strong> Eferding, Austria <\/strong><br/> Number of lawyers:  9 <\/p>","<p><strong> Freistadt, Austria <\/strong><br/> Number of lawyers:  9 <\/p>","<p><strong> Fürstenfeld, Austria <\/strong><br/> Number of lawyers:  9 <\/p>","<p><strong> Gänserndorf, Austria <\/strong><br/> Number of lawyers:  9 <\/p>","<p><strong> Gleisdorf, Austria <\/strong><br/> Number of lawyers:  9 <\/p>","<p><strong> Horn, Austria <\/strong><br/> Number of lawyers:  9 <\/p>","<p><strong> Mattighofen, Austria <\/strong><br/> Number of lawyers:  9 <\/p>","<p><strong> Saalfelden, Austria <\/strong><br/> Number of lawyers:  9 <\/p>","<p><strong> Traun, Austria <\/strong><br/> Number of lawyers:  9 <\/p>","<p><strong> Wolfsberg, Austria <\/strong><br/> Number of lawyers:  9 <\/p>","<p><strong> Bruck/Leitha, Austria <\/strong><br/> Number of lawyers:  8 <\/p>","<p><strong> Hartberg, Austria <\/strong><br/> Number of lawyers:  8 <\/p>","<p><strong> Klosterneuburg, Austria <\/strong><br/> Number of lawyers:  8 <\/p>","<p><strong> Neusiedl/See, Austria <\/strong><br/> Number of lawyers:  8 <\/p>","<p><strong> Oberpullendorf, Austria <\/strong><br/> Number of lawyers:  8 <\/p>","<p><strong> Bad Ischl, Austria <\/strong><br/> Number of lawyers:  7 <\/p>","<p><strong> Bischofshofen, Austria <\/strong><br/> Number of lawyers:  7 <\/p>","<p><strong> Hard, Austria <\/strong><br/> Number of lawyers:  7 <\/p>","<p><strong> Lambach, Austria <\/strong><br/> Number of lawyers:  7 <\/p>","<p><strong> Liezen, Austria <\/strong><br/> Number of lawyers:  7 <\/p>","<p><strong> Melk, Austria <\/strong><br/> Number of lawyers:  7 <\/p>","<p><strong> Mistelbach, Austria <\/strong><br/> Number of lawyers:  7 <\/p>","<p><strong> Schwechat, Austria <\/strong><br/> Number of lawyers:  7 <\/p>","<p><strong> Stockerau, Austria <\/strong><br/> Number of lawyers:  7 <\/p>","<p><strong> Waidhofen/Thaya, Austria <\/strong><br/> Number of lawyers:  7 <\/p>","<p><strong> Enns, Austria <\/strong><br/> Number of lawyers:  6 <\/p>","<p><strong> Feldkirchen, Austria <\/strong><br/> Number of lawyers:  6 <\/p>","<p><strong> Herzogenburg, Austria <\/strong><br/> Number of lawyers:  6 <\/p>","<p><strong> Hollabrunn, Austria <\/strong><br/> Number of lawyers:  6 <\/p>","<p><strong> Köflach, Austria <\/strong><br/> Number of lawyers:  6 <\/p>","<p><strong> Leonding, Austria <\/strong><br/> Number of lawyers:  6 <\/p>","<p><strong> Mondsee, Austria <\/strong><br/> Number of lawyers:  6 <\/p>","<p><strong> St. Johann/Tirol, Austria <\/strong><br/> Number of lawyers:  6 <\/p>","<p><strong> Völkermarkt, Austria <\/strong><br/> Number of lawyers:  6 <\/p>","<p><strong> Altheim, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Altmünster, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Feldbach, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Fügen, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Gmünd, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Graz-Seiersberg, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Judenburg, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Kirchberg, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Knittelfeld, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Lustenau, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Mattersburg, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Reutte, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Ried im Innkreis, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Scheibbs, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Schruns, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> St. Johann/Pongau, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> St. Valentin, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Weiz, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Zwettl, Austria <\/strong><br/> Number of lawyers:  5 <\/p>","<p><strong> Altenmarkt, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Bad Aussee, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Bad Hofgastein, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Eugendorf, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Haag, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Kapfenberg, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Kirchdorf/Krems, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Mannersdorf, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Micheldorf, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Murau, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Neulengbach, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Perg, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Premstätten, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Rankweil, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Rattenberg/Inn, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> St. Florian/Linz, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Velden/Wörthersee, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Voitsberg, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Vorchdorf, Austria <\/strong><br/> Number of lawyers:  4 <\/p>","<p><strong> Bad Schallerbach, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Berndorf, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Ebensee, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Elsbethen, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Gunskirchen, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Güssing, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Hermagor, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Hohenems, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Kremsmünster, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Lochau, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Marchtrenk, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Mauthausen, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Mayrhofen, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Mittersill, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Mürzzuschlag, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Oberndorf, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Pöchlarn, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Purkersdorf, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Radstadt, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Retz, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Rohrbach, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Schwanenstadt, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Schwertberg, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Seekirchen, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Tamsweg, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Waidhofen/Ybbs, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Windischgarsten, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Ybbs/Donau, Austria <\/strong><br/> Number of lawyers:  3 <\/p>","<p><strong> Andorf, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Anif, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Bad Goisern, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Bad Häring, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Bad Vöslau, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Bezau, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Bleiburg, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Brunn/Gebirge, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Ebreichsdorf, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Eibiswald, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Fehring, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Ferlach, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Frastanz, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Friesach, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Frohnleiten, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Gnas, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Gössendorf, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Gratwein-Straßengel, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Gratwein, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Gröbming, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Groß-Enzersdorf, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Hainfeld, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Hart bei Graz, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Irdning, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Jennersdorf, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Kaindorf an der Sulm, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Kirchbichl, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Kramsach, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Krumpendorf, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Kundl, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Laa/Thaya, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Laakirchen, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Langenzersdorf, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Lieboch, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Lilienfeld, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Mils bei Imst, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Peuerbach, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Pressbaum, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Ramsau im Zillertal, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Rohrbach-Berg, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Röthis, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Rottenmann, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Schlüßlberg, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Schwarzach/Pongau, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Silz, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> St. Florian, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Strasswalchen, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Sulz, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Wiener Neudorf, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Wieselburg, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Wilhelmsburg, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Wolkersdorf, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Zell am Ziller, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Zell/Ziller, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Zistersdorf, Austria <\/strong><br/> Number of lawyers:  2 <\/p>","<p><strong> Absam, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Achenkirch, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Althofen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Altlengbach, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Asten, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Bad Gastein, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Bad Hall, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Bad Kleinkirchheim, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Bad Radkersburg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Bärnbach, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Bergheim, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Bludenz-Bürs, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Böheimkirchen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Bruck an der Großglocknerstr., Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Bruckneudorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Brunn am Gebirge, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Buch bei Jenbach, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Deutschfeistritz, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Dobersberg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Döbriach, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Eben/Pongau, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Egg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Eggelsberg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Eggendorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Ehrwald, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Eichgraben, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Fischlham, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Frankenburg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Frankenmarkt, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Frauenkirchen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Fulpmes, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Gablitz, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Gallneukirchen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Gaming, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Gars am Kamp, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Garsten, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Gerersdorf/St. Pölten, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Gießhübl, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Göfis, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Golling, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Grein, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Grödig, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Groß Gerungs, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Guntramsdorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Haid/Ansfelden, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Hainburg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Hausmannstätten, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Heiligenkreuz am Waasen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Henndorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Hinterbrühl, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Hirschegg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Höchst, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Hof, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Höfen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Hohenzell, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Hopfgarten, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Illmitz, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Innsbruck-Igls, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Jois, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Kalsdorf bei Graz, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Kaprun, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Kematen in Tirol, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Kindberg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Kirchberg/Wagram, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Klosterneuburg-Kritzendorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Lans, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Lauterach, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Lebring, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Lenzing, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Leobersdorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Leutasch, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Ludesch, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Markt Hartmannsdorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Matrei/Osttirol, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Mauerbach, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Mauerkirchen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Mieming, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Münster, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Mureck, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Nebersdorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Neudauberg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Neufelden, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Neuhofen/Krems, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Neumarkt im Hausruckkreis, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Neusiedl am See, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Neuzeug, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Nußdorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Nüziders, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Obertrum/See, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Ohlsdorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Ottensheim, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Pasching, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Paudorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Pettenbach, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Pettendorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Pfaffstätten, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Pfarrwerfen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Pichl bei Wels, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Pöls-Oberkurzheim, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Pöndorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Pörtschach am Wörther See, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Pöttsching, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Pregarten, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Raaba-Grambach, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Rauris, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Regau, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Reifnitz, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Reith/Kitzbühel, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Rekawinkel, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Riegersburg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Rosental an der Kainach, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Rudersdorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Rum, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Scharnstein, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Schlins, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Seeboden, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Seefeld in Tirol, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Seiersberg-Pirka, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Seiersberg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Seitenstetten, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Siegenfeld, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Siezenheim, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Sinabelkirchen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Söll, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> St. Andrä-Wördern, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> St. Gilgen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> St. Martin im Innkreis, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> St. Martin in der Wart, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> St. Michael, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> St. Paul, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Stadl-Paura, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Stainz, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Stallhofen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Stattegg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Stegersbach, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Steinach/Brenner, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Steyregg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Stoob, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Ternitz, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Thalgau, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Thalheim  bei Wels, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Thalheim/Wels, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Thüringerberg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Traiskirchen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Traunkirchen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Trofaiach, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Uderns, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Volders, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Völs, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Vorderthiersee, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Wattens, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Weigelsdorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Weißkirchen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Werfen, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Werfenweng, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Westendorf, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Wildon, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Zeiselmauer, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Zeltweg, Austria <\/strong><br/> Number of lawyers:  1 <\/p>","<p><strong> Zirl, Austria <\/strong><br/> Number of lawyers:  1 <\/p>"],{"interactive":false,"permanent":false,"direction":"auto","opacity":1,"offset":[0,0],"textsize":"15px","textOnly":false,"style":{"font-weight":"normal","padding":"3px 8px","color":"#00A08A"},"className":"","sticky":true},null]}],"setView":[[47.4968,13.5306],7,[]],"limits":{"lat":[46.5265324,48.9160904],"lng":[9.5981724,16.9422459]}},"evals":[],"jsHooks":[]}</script>

Data looks beautiful!!!

You can now also display in a map the geographical distribution of other available data. For example, cities with the higher percentage of registered individuals registered with e-mail contacts or cities with the higher percentage of lawyers with websites personalized websites, among others.
