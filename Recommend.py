    
    
def findClosestCritics(cri_ratings, per_ratings):
    '''this function is used to identify three critics, whose recommendations are 
    closest to the person’s recommendations. There are two parameters of type DataFrame: 
    critics ratings, and personal ratings. The function returns a list of three critics, 
    whose ratings of movies are most similar to those provided in the personal ratings data, 
    based on Euclidean distance.'''
    
    #set the Title as index to make the following subtraction
    indcrating = cri_ratings.set_index('Title')
    indprating = per_ratings.set_index('Title')
     
    #transform the ratings into integer
    indcrating.astype('int64')
    indprating.astype('int64')
     
    #subtract the ratings of person from each of the critics with title \
    #as the index and critics' name as columns' name
    diffData = indcrating.subtract(indprating.iloc[:, 0], axis = 0)
     
    #square and then sum the value in each column, ignore null values
    distance = (diffData.loc[:,:] ** 2).sum(axis = 0, skipna = True)
    diffData.loc['distance'] = distance
    diffData = diffData.sort_values(by = ['distance'], axis = 1)
    criticname = list(diffData.columns[ :3])
    
    return criticname



def recommendMovies(cri_ratings, per_ratings, clsCritics, moviedf):
    '''this function is used to generate movie recommendations based on ratings by the 
    chosen critics. The function accepts four parameters: the critics and personal ratings 
    data frames, the list of three critics most similar to the person, and the movie data frame.
    The function determines out of the set of movies that are not rated in the personal data, 
    but are rated by the critics, which movies have the highest average of the rating by the 
    most similar critics in each movie genre (specified by the Genre1 column of movie data), 
    which are the top-rated unwatched movies in each genre category, based on the average of 
    the three critics’ ratings.'''
    
    
    import pandas as pd
    
    #get rid of those ratings that are not from the three closest critics
    clsCritics.insert(0, 'Title')
    clscriratings = cri_ratings.loc[:,clsCritics]
    
    #calculate the average of the ratings from the three closest critics
    clscriratings['rating'] = round(clscriratings.mean(axis = 1, skipna = True),2)

    #merge the person's data and closest critics' data
    mergeRating = pd.merge(clscriratings, per_ratings, how = 'left', on = 'Title')
    
    #create a column to denote if the movie has been watched by the person
    mergeRating['isna'] = mergeRating.iloc[:,-1].isna()
    
    #drop those rows that don't contain NaN in the person's rating column
    unwatchedMovie = mergeRating[mergeRating['isna'] == True]
    
    #merge the movie data with the rating data
    movinfo = pd.merge(unwatchedMovie, moviedf, how = 'inner', on = 'Title')
#     movinfo = movinfo.loc[:,:'Budget']
#     print(movinfo.head())
    
    movinfo['g1'] = movinfo['Genre1']
    
    #group the average ratings by the genre1
    pd.set_option('display.max_columns', 1000) 
    gbGenre1 = movinfo.groupby(by = 'g1')
    
    #store the maximum ratings in a Series
    genermax = gbGenre1.max()['rating']
    
    #select those movies in each genre that are equal or higher than the rating
    recommendM = pd.DataFrame()
    
    #find the max rating from critics for each genre1, find the movie ratings higher than that
    for i in range(len(genermax)):
        grpdf = gbGenre1.get_group(genermax.index[i])

        row = grpdf[grpdf['rating'] >= genermax.iloc[i]]

        recommendM = recommendM.append(row)
    
    recommendM.sort_values(by = ['Genre1'], ascending = True)
    
    #generate a new dataframe for later printing
    printout = recommendM.loc[:,['Title', 'Genre1', 'rating', 'Year', 'Runtime']]
    printout = printout.fillna(' ')
    print(printout.head())
    
    return printout



def printRecommendations(rcmmdMv, pname):
    '''this function accepts two parameters: the first containing information about the 
    recommended movies, and the second is the name of the person. The function must produce 
    a printout of all recommendations passed in via the first parameter, in alphabetical 
    order by the genre.'''
    
    
    #print out the three closest critics to the person's rating
    print('Recommendations for', (pname + ':'))
    
    #calculate the max length of the movie title for later format
    titlelst = rcmmdMv.Title.tolist()
    titlelen = [len(i) for i in titlelst]
    maxlen = max(titlelen) + 5
    
    #print movie information of every recommended movie
    for row in range(len(rcmmdMv.index)):
        print(('"' + rcmmdMv.iloc[row, 0] + '"').ljust(maxlen), end = '')
        print('(' + rcmmdMv.iloc[row, 1] + ')', end = ', ')
        print('rating:', str(rcmmdMv.iloc[row, 2]), end = ', ')
        
        #to take care of null value when printing
        if rcmmdMv.iloc[row, -1] != ' ':
            print(str(rcmmdMv.iloc[row, 3]), end = ', ')
            print('runs', rcmmdMv.iloc[row, 4])
            
        else:
            print(str(rcmmdMv.iloc[row, 3]))



def main():
    '''Created by Joann, Nov 24, 2019
    The task of this function is to create movie recommendations for a person, based 
    on the match between personal ratings and critics’ ratings of the movies.'''
    
    
    import pandas as pd
    import os
    
    #1. Ask the user to specify the subfolder in the current working directory, where 
    #the files are stored, along with the names of the movies, critics, and person data files.
    mvfolder, mvfile, crifile, personfile = input('Please enter the name of the folder with files, \
the name of movies file, \nthe name of critics file, the name of personal ratings file, \
separated by spaces:\n').strip().split()
    
    newcwd = os.path.join(os.getcwd(), mvfolder)
    os.chdir(newcwd)
    
    rating = pd.read_csv(crifile)
    perRating = pd.read_csv(personfile)
    
    #2. Determine and output the names of three critics, whose ratings of the movies are closest 
    #to the person’s ratings based on the Euclidean distance metric.
    clscri = findClosestCritics(rating, perRating)
    print('\nThe following critics had reviews closest to the person\'s:')
    for name in clscri[:-1]:
        print(name, end = ', ')
    print(clscri[-1])
    print()

    
    moviedf = pd.read_csv(mvfile, encoding = "ISO-8859-1")
    
    #3. Use the ratings by the critics identified in stpe 2 to determine which movies to recommend.
    recommendDF = recommendMovies(rating, perRating, clscri, moviedf)

    
    personname = perRating.columns[1]
    
    #Display information about recommended movies
    printRecommendations(recommendDF, personname)


main()


#data-tiny tinyIMDB.csv tinyratings.csv tinyp.csv
#data IMDB.csv ratings.csv p8.csv