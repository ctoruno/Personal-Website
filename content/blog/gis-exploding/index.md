---
author: Carlos A. Toruño P.
date: "2023-07-29"
draft: false
excerpt: Some geographical data sources include Taiwan as part of China. In this post, I show you how to split these territories without having to use other data source.
subtitle: ""
weight: 1
title: Exploding geometries with GeoPandas
subtitle: Applied to the Taiwan and China scenario
layout: single
tags:
- GIS
- China
- Taiwan
---

In my [previous blog post](https://www.carlos-toruno.com/blog/streamlit/01-intro/), I showed how to program a choropleth map generator using Streamlit. While doing this, I encountered an issue I had never experienced before. More specifically, how to explode geometries. As you might know, there is a huge international debate about Taiwan being a sovereign country. As a result, many "*official*" datasets containing world boundaries would usually include the island of Taiwan as part of China. The big question that relates to this blog post is, how can we split the boundaries between these two territories? Therefore, in this blog post, I will be explaining to you how I solved this issue using the [GeoPandas library](https://geopandas.org/en/stable/) in Python.

<img src="featured.png" width="100%"/>

## A little bit of context
Since the approval of the [resolution 2758(XXVI)](https://undocs.org/en/A/RES/2758(XXVI)) by the United Nations back in 1971, Taiwan has been excluded from many international circles. Taiwan does not have a seat in the United Nations since their representatives were expelled after the approval of this resolution. At the same time, if you search for Taiwan in the [list of countries and economies](https://data.worldbank.org/country) in the World Bank Data portal, you won't find it.

To be honest, I have been reading a lot about this issue and I have found it to be very interesting. For example, the UN resolution states that "(...) the representatives of the Government of the People's Republic of China are the only lawful representatives of China", not that Taiwan is not a country. Which is a very important highlight if you want to use this resolution in favor of the "One-China policy". This has opened a very interesting diplomatic strategy for the Government of Taipei in trying to highlight the difference between China and Taiwan. If you would like to read about this in more depth, I would suggest you to read [this article](https://verfassungsblog.de/taiwan-and-the-myth-of-un-general-assembly-resolution-2758/) by prof. Chien-Huei Wu. 

This approach is even mmore interesting when you take a look at the data from public opinion polls. According to the National Chengchi University, less than 20% of the population living in the island considered themselves Taiwanese back in 1992, while more than 70% considered themselves chinese or both. Thirty years later, almost 65% of the population considered themselves taiwanese and not chinese (check [this article](https://www.bbc.com/news/world-asia-china-59900139) by the BBC for more interesting data).

Now, as I stated in my [previous blog post](https://www.carlos-toruno.com/blog/streamlit/01-intro/), I intended to use the [World Bank Official Boundaries Data](https://datacatalog.worldbank.org/search/dataset/0038272/World-Bank-Official-Boundaries), and I still do. So, let's take a look at the data, let's subset China and see how it looks in a map.


```python
import geopandas as gpd

# Loading World Bank Official Boundaries
raw_boundaries  = (gpd.read_file("WB_countries_Admin0.geojson"))

# Subsetting China -> Code "CHN"
china    = raw_boundaries.loc[raw_boundaries["WB_A3"] == "CHN"]

# Plotting the geometries
china.plot().set_axis_off()
```


    
![png](output_1_0.png)
    


I hope your geography knowledge is outstanding, but in case you are a little bit lost...

Do you see that small island in the southeast, that's Taiwan! And it should not be displayed in this map because we were ONLY subsetting the geometries that belong to country code CHN, in other words, the People's Republic of China. And given that there is nno listed country code for Taiwan in the documentation, we can assume that these data follow the "One China" policy. Sad, I know. So, how do we solve this?

## Possible solutions

The most logical solution that many of you would propose is to use a subnational boundaries or a ADM-1 level data. Sadly (but not surprising), the World Bank does not supply an official licensed ADM-1 data for subnational boundaries. Then, why don't we use any other data source like our beloved [geoBoundaries](https://www.geoboundaries.org/)? As it happens, I need an official source for the map generator app, preferrably from the United Nations or the World Bank. Don't ask too many questions.

Some of you will suggest me to solve this issue using ArcGIS or QGIS. However, and let's be honest, I refuse to do this without coding. So, I just asked Google about how could I split a geometry and I quickly found something called "*exploding*". Which, is a terrible name to be honest.

But, to be quite academic, exploding a geometry means to break a feature into its individual parts. This means that, if you have a multipolygon, you would end up with multiple individual and differentiable polygons. But if you have a polygon, you would end up  with multiple individual and differentiable lines, and so on. The most important part, is that each of these splitted parts would be a different feature by itself. The Geopandas library comes with aa native API function that allows us to do this.

## Using GeoPandas to explode geometries

Given that country boundaries are multipolygon features, if we were to explode China (the geometry, not the country), we should end up with a geopandas data frame containing the continental part of the country and all its islands, which are quite numerous. Let's see what happens.

First, let's take a look at our current subset for China:


```python
china[["TYPE", "WB_A3", "NAME_EN", "geometry"]]
```

<table width="100%">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>TYPE</th>
      <th>WB_A3</th>
      <th>NAME_EN</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8</th>
      <td>Country</td>
      <td>CHN</td>
      <td>People's Republic of China</td>
      <td>MULTIPOLYGON (((110.68507 20.15331, 110.67791 ...</td>
    </tr>
  </tbody>
</table>



As we can observe, we currently have a single-row geo-dataframe and its geometry states that it is a multipolygon. That means that if we explode this subset, we should en up with a geo data frame listing all of its polygons. Let's see if that's the case:


```python
## Exploding China's geometry
china_ex = (china[["TYPE", "WB_A3", "CONTINENT", 
                   "REGION_UN", "SUBREGION", "REGION_WB", 
                   "NAME_EN", "WB_NAME", "WB_REGION", 
                   "geometry"]]
            .explode(index_parts = True)
            .reset_index(drop = True))

## How does the new geo-data-frame look like?
china_ex
```

<table>
  <style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

    table {
      display: block;
      overflow-x: auto;
      white-space: nowrap;
    }
  </style>
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>TYPE</th>
      <th>WB_A3</th>
      <th>CONTINENT</th>
      <th>REGION_UN</th>
      <th>SUBREGION</th>
      <th>REGION_WB</th>
      <th>NAME_EN</th>
      <th>WB_NAME</th>
      <th>WB_REGION</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Country</td>
      <td>CHN</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>POLYGON ((110.68507 20.15331, 110.67791 20.163...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Country</td>
      <td>CHN</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>POLYGON ((110.44264 20.66352, 110.43702 20.667...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Country</td>
      <td>CHN</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>POLYGON ((110.60955 20.89728, 110.62452 20.915...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Country</td>
      <td>CHN</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>POLYGON ((109.10524 21.02448, 109.11256 21.027...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Country</td>
      <td>CHN</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>POLYGON ((110.38982 21.09589, 110.37135 21.080...</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>66</th>
      <td>Country</td>
      <td>CHN</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>POLYGON ((122.74195 39.23607, 122.71860 39.241...</td>
    </tr>
    <tr>
      <th>67</th>
      <td>Country</td>
      <td>CHN</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>POLYGON ((122.68442 39.26219, 122.66326 39.272...</td>
    </tr>
    <tr>
      <th>68</th>
      <td>Country</td>
      <td>CHN</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>POLYGON ((121.35255 39.48241, 121.34059 39.481...</td>
    </tr>
    <tr>
      <th>69</th>
      <td>Country</td>
      <td>CHN</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>POLYGON ((123.02996 39.50788, 123.04005 39.529...</td>
    </tr>
    <tr>
      <th>70</th>
      <td>Country</td>
      <td>CHN</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>POLYGON ((123.47141 53.51901, 123.43167 53.535...</td>
    </tr>
  </tbody>
</table>
<p>71 rows × 10 columns</p>


```python
china_ex.plot(column="geometry").set_axis_off()
```


    
![png](output_6_0.png)
    


As we can see, we now have a geo data frame with 71 rows. However, there is no way for us to know which feature is what. If we plot the data and color different features with different colors, we are only able to distinguish the three larger ones: continental China, the island of Taiwan, and the island of Hainan, respectively. Therefore, we need to highlight the second larger polygon. We can do this by estimating the area and subsetting


```python
# Create a new column to store the area values
china_ex["area_m2"] = (china_ex
                       .to_crs("ESRI:54003")
                       .geometry
                       .area)

## Sorting values
china_exsort = china_ex.sort_values(by = "area_m2", 
                                    ascending = False)

## Which row index represents Taiwan?
china_exsort.iloc[1:2]
```

<table>
  <style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

    table {
      display: block;
      overflow-x: auto;
      white-space: nowrap;
    }
  </style>
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>TYPE</th>
      <th>WB_A3</th>
      <th>CONTINENT</th>
      <th>REGION_UN</th>
      <th>SUBREGION</th>
      <th>REGION_WB</th>
      <th>NAME_EN</th>
      <th>WB_NAME</th>
      <th>WB_REGION</th>
      <th>geometry</th>
      <th>area_m2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>31</th>
      <td>Country</td>
      <td>CHN</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>POLYGON ((121.63600 25.22281, 121.59791 25.271...</td>
      <td>4.153658e+10</td>
    </tr>
  </tbody>
</table>


As we can observe, Taiwan is the feature with row index 31 in the data frame. We could confirm this visually by plotting this feature alone. Again, I'm assuming that you have outstanding geography notions my dear padawan. But if you don't, here you have the mapped feature that we got and a google maps image of how should Taiwan look like . If they look alike, probably we are doing things right.

```python
china_exsort.iloc[1:2].plot().set_axis_off()
```

<style>
  .row {display: flex;}
  .column {flex: 50%;}
</style>

<div class="row">
  <div class="column">
    <img src="output_10_0.png" width="40%"/>
  </div>
  <div class="column">
    <img src="taiwan_google.png" width="40%"/>
  </div>
</div>

We have been succesfully been able to identify Taiwan, what do we do now? Well, we basically need to rejoin all the other islands back to China, remove the China/Taiwan feature from our boundaries data, and add the exploded data with China and Taiwan as separate features. Sounds complex, right? Well, it's actually quite straightforward. Let's go step by step.

First, we need to manually input Taiwan's country data as follows:


```python
# Manually inputting Taiwan's info
china_ex.at[31, 'WB_A3']   = "TWN"
china_ex.at[31, 'NAME_EN'] = "Taiwan"
china_ex.at[31, 'WB_NAME'] = "Taiwan"
```

Once we have inputed that data, we can dissolve the geometries to form a simplified data frame. If you are wondering what do I mean by dissolving, it's bassically the opposite of exploding. Still not great naming skills, I know. We want to aggregate (or dissolve) all those islands to the same feature as continental China. Except for Taiwan, of course.


```python
# Disolving exploded geopandas for China
china_taiwan = (china_ex
                .dissolve(by      = "WB_A3",
                          aggfunc = "first")).reset_index()

china_taiwan
```

<table>
  <style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

    table {
      display: block;
      overflow-x: auto;
      white-space: nowrap;
    }
  </style>
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>WB_A3</th>
      <th>geometry</th>
      <th>TYPE</th>
      <th>CONTINENT</th>
      <th>REGION_UN</th>
      <th>SUBREGION</th>
      <th>REGION_WB</th>
      <th>NAME_EN</th>
      <th>WB_NAME</th>
      <th>WB_REGION</th>
      <th>area_m2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>CHN</td>
      <td>MULTIPOLYGON (((110.86988 19.99702, 110.89015 ...</td>
      <td>Country</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>People's Republic of China</td>
      <td>China</td>
      <td>EAP</td>
      <td>3.727520e+10</td>
    </tr>
    <tr>
      <th>1</th>
      <td>TWN</td>
      <td>POLYGON ((121.63600 25.22281, 121.59791 25.271...</td>
      <td>Country</td>
      <td>Asia</td>
      <td>Asia</td>
      <td>Eastern Asia</td>
      <td>East Asia &amp; Pacific</td>
      <td>Taiwan</td>
      <td>Taiwan</td>
      <td>EAP</td>
      <td>4.153658e+10</td>
    </tr>
  </tbody>
</table>


Once that we have China and Taiwan as different features, we proceed to append this new data to our world boundaries. Don't forget to drop the previous China feature!!!


```python
import pandas as pd

# Appending china+taiwan geopandas to raw_boundaries
raw_boundaries = (pd.concat([raw_boundaries.loc[raw_boundaries["WB_A3"] != "CHN"],
                             china_taiwan],
                             ignore_index = True))
```

This way, we have been able to split China and Taiwan as separate features without having to change our source data and just with a few lines of code.
