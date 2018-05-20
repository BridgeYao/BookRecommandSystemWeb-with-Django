from django.shortcuts import render,redirect,reverse

from django.http import HttpResponse, HttpResponseRedirect

from bookRecommand.models import  LoginForm
import bookRecommand
from DataBaseManagement.database import MyDataBase
from modeles.Book import Book
import re
#=========================================
# 首页
#=========================================
def index(request):
    return render(request,'bookRecommand/bookSearch.html')

def detail(request,**kwargs):
    data = {
        'postnumber':kwargs['pk']
    }
    return render(request,'bookRecommand/detail.html',context=data)

#======================================
# 进行登录操作
#======================================
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            request.session['isLogin'] = True
            request.session['user'] = form.data['username']
    return redirect(reverse(bookRecommand.views.index))

# 退出登录操作
def quitLogin(request):
    request.session['isLogin'] = False
    request.session['user'] = ''
    return redirect(reverse(bookRecommand.views.index))
#=======================================
# 搜索功能
#======================================
def search(request):
    csrfmiddlewaretoken = request.GET.get('csrfmiddlewaretoken',None)
    findCode = request.GET.get('find_code','AllKeyButNotCatalog')
    searchKey = request.GET.get('searchKey',None)
    sortKey = request.GET.get('sort','Year-Rating-Person')
    page = int(request.GET.get('page',0))
    year = request.GET.get('year',None)     # 用于检索条件的年份显示
    years = {}             # 用于侧边栏的年份显示

    if not csrfmiddlewaretoken or not searchKey:
        return redirect(reverse(bookRecommand.views.index))


    database = MyDataBase()
    books = []

    # 判断查询码，构建查询字典
    if findCode == 'AllKeyButNotCatalog':
        findData = {'$or':[
            {'bookName':{'$regex':searchKey,'$options':'i'}},
            {'content': {'$regex': searchKey, '$options': 'i'}},
            {'author': {'$regex': searchKey, '$options': 'i'}},
            {'ISBN': {'$regex': searchKey, '$options': 'i'}},
            {'publishYear': {'$regex': searchKey, '$options': 'i'}},
            {'index': {'$regex': searchKey, '$options': 'i'}},
            {'publisher': {'$regex': searchKey, '$options': 'i'}},
            {'systemNumber': {'$regex': searchKey, '$options': 'i'}}
        ]}
    elif findCode == 'AllKey':
        findData = {'$or':[
            {'catalog': {'$regex': searchKey, '$options': 'i'}},
            {'bookName':{'$regex':searchKey,'$options':'i'}},
            {'content': {'$regex': searchKey, '$options': 'i'}},
            {'author': {'$regex': searchKey, '$options': 'i'}},
            {'ISBN': {'$regex': searchKey, '$options': 'i'}},
            {'publishYear': {'$regex': searchKey, '$options': 'i'}},
            {'index': {'$regex': searchKey, '$options': 'i'}},
            {'publisher': {'$regex': searchKey, '$options': 'i'}},
            {'systemNumber':{'$regex': searchKey, '$options': 'i'}}
        ]}
    elif findCode == 'CatalogKey':
        findData = {'catalog': {'$regex': searchKey, '$options': 'i'}}
    elif findCode == 'BookNameKey':
        findData = {'bookName': {'$regex': searchKey, '$options': 'i'}}
    elif findCode == 'BookAuthorKey':
        findData = {'author': {'$regex': searchKey, '$options': 'i'}}
    elif findCode == 'BookPublisherKey':
        findData = {'publisher': {'$regex': searchKey, '$options': 'i'}}
    elif findCode == 'ISBNKey':
        findData = {'ISBN': {'$regex': searchKey, '$options': 'i'}}
    elif findCode == 'IndexKey':
        findData = {'index': {'$regex': searchKey, '$options': 'i'}}
    elif findCode == 'SystemNumberKey':
        findData = {'systemNumber':{'$regex': searchKey, '$options': 'i'}}
    else:
        findData = {'$or':[
            {'bookName':{'$regex':searchKey,'$options':'i'}},
            {'content': {'$regex': searchKey, '$options': 'i'}},
            {'author': {'$regex': searchKey, '$options': 'i'}},
            {'ISBN': {'$regex': searchKey, '$options': 'i'}},
            {'publishYear': {'$regex': searchKey, '$options': 'i'}},
            {'index': {'$regex': searchKey, '$options': 'i'}},
            {'publisher': {'$regex': searchKey, '$options': 'i'}},
            {'systemNumber': {'$regex': searchKey, '$options': 'i'}}
        ]}

    # 如果使用年份作为缩小范围
    if year != None:
        findData['publishYear'] = int(year)

    # 判断排序方法
    if sortKey == 'Year-Rating-Person':
        print('按照年份-评分-评论人数降序排序')
        result = database.collections.find(findData).\
            sort([('publishYear', -1),('ratingAverage', -1),('ratingNumberRaters', -1)]).\
            skip(page * 10).\
            limit(10)
    elif sortKey == 'Rating-Year-Person':
        print('按照评分-年份-评论人数降序排序')
        result = database.collections.find(findData).\
            sort([('ratingAverage', -1),('publishYear', -1),('ratingNumberRaters', -1)]).\
            skip(page * 10).\
            limit(10)
    elif sortKey == 'Person-Year-Rating':
        print('按照评论人数-年份-评分-降序排序')
        result = database.collections.find(findData).\
            sort([('ratingNumberRaters', -1),('publishYear', -1),('ratingAverage', -1)]).\
            skip(page * 10).\
            limit(10)
    else:
        print('else的情况')
        result = database.collections.find(findData).\
            sort([('publishYear', -1),('ratingAverage', -1),('ratingNumberRaters', -1)]).\
            skip(page * 10).\
            limit(10)

    count = 0
    for data in result:
        ratingGraphic = []
        for i in range(0,5):
            if i < data.get('ratingAverage',-1)//2:
                 ratingGraphic.append([count,'true'])
            else:
                ratingGraphic.append([count,'false'])
            count += 1
        # 缩短书名
        bookName = data.get('bookName', '')
        bookName = bookName.split()[0]

        book = Book(ISBN=data.get('ISBN',''),
                    bookName=bookName,
                    bookUrl=data.get('bookUrl',''),
                    author=data.get('author',''),
                    content=data.get('content',''),
                    publishYear=data.get('publishYear',-1),
                    bookIndex=data.get('index',''),
                    publisher=data.get('publisher',''),
                    catalog=data.get('catalog',''),
                    douBanId=data.get('douBanId',''),
                    doubanRating=data.get('ratingAverage',-1),
                    doubanRatingPerson=data.get('ratingNumberRaters',-1),
                    doubanSummary=data.get('doubanSummary',''),
                    seriesTitle=data.get('seriesTitle',''),
                    systemNumber=data.get('systemNumber',''),
                    ratingGraphic=ratingGraphic)
        books.append(book)
        years[book.publishYear] = years.get(book.publishYear,0)+1

    # 本次搜索一共有多少条记录
    totalCount = result.count()
    # 总页数
    totalPage = totalCount//10

    # 分页的范围
    start = 0 if page-5<0 else page-5
    end = totalPage if page+5>totalPage else page+5
    pageRange = range(start,end)

    database.client.close()

    context = {
        'findCode':findCode,
        'books':books,
        'searchKey':searchKey,
        'page':page,
        'csrf':csrfmiddlewaretoken,
        'totalCount':totalCount,
        'totalPage':totalPage,
        'range':pageRange,
        'years':years.keys()
    }
    return render(request,'bookRecommand/bookSearch.html',context=context)

#=======================================
# 书籍详情页面的显示
# 根据ISBN号找到书名
#========================================
def bookDetail(request,ISBN):
    database = MyDataBase()

    data = database.collections.find_one({'ISBN':ISBN})
    #=================================================
    # 下面是一本书的详细信息
    #=================================================
    ratingGraphic = []
    count = 0
    for i in range(0, 5):
        if i < data.get('ratingAverage', -1) // 2:
            ratingGraphic.append([count, 'true'])
        else:
            ratingGraphic.append([count, 'false'])
        count += 1
    # 缩短书名
    bookName = data.get('bookName', '')
    bookName = bookName.split()[0]
    book = Book(ISBN=data.get('ISBN', ''),
                bookName=bookName,
                bookUrl=data.get('bookUrl', ''),
                author=data.get('author', ''),
                content=data.get('content', ''),
                publishYear=data.get('publishYear', -1),
                bookIndex=data.get('index', ''),
                publisher=data.get('publisher', ''),
                catalog=data.get('catalog', ''),
                douBanId=data.get('douBanId', ''),
                doubanRating=data.get('ratingAverage', -1),
                doubanRatingPerson=data.get('ratingNumberRaters', -1),
                doubanSummary=data.get('doubanSummary', ''),
                seriesTitle=data.get('seriesTitle', ''),
                systemNumber=data.get('systemNumber', ''),
                ratingGraphic=ratingGraphic)
    database.client.close()
    context = {
        'book':book
    }
    return render(request,'bookRecommand/bookDetail.html',context=context)

#========================================
# 真正的首页
#========================================
def trueIndex(request):
    return render(request,'bookRecommand/index.html')

import json
#======================================
# 用于测试
#=======================================
def _test(request):
    context = {
        'book':Book(bookName='sjm',ratingGraphic=[[0, 'false'], [1, 'false'], [2, 'false'], [3, 'false'], [4, 'false']])
    }
    # context = json.dumps(context)
    return render(request,'bookRecommand/test.html',context=context)
