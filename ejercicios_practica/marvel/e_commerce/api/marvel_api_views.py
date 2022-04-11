# Import models:
from e_commerce.models import *

from marvel.settings import VERDE, CIAN, AMARILLO
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import hashlib

# NOTE: Declaramos las variables que tienen que ver con la API KEY de Marvel:

PUBLIC_KEY = '58ee40376f7c10e99f440f5e3abd2caa'
PRIVATE_KEY = '2c0373e00d85edb4560f68ddc2094014e8694f90'
TS = 1
TO_HASH = str(TS)+PRIVATE_KEY+PUBLIC_KEY
HASHED = hashlib.md5(TO_HASH.encode())
URL_BASE = 'http://gateway.marvel.com/v1/public/'
ENDPOINT = 'comics'
ENDPOINT_CHARACTER = 'characters'
PARAMS = dict(ts=TS, apikey=PUBLIC_KEY, hash=HASHED.hexdigest())


@csrf_exempt
def get_comics(request):
    '''
    Vista personalizada de API para comprar comics, 
    primero consultamos los comics disponibles en la página de Marvel, 
    luego generamos una lista de los que tienen precio y descripción, 
    porque varios vienen `null`.
    '''
    # Declaramos nuestras variables:
    id = []
    title = []
    description = []
    prices = []
    thumbnail = []
    limit = 0
    offset = 0
    # NOTE: Para obtener los valores de request, dependemos del tipo de petición, así:
    # GET METHOD: request.GET['algo']   O también: request.GET.get('algo')
    # POST METHOD: request.POST['algo'] O también: request.POST.get('algo')
    # POST METHOD: request.data['algo'] O también: request.data.get('algo')
    # Como son similares a los diccionarios se puede hacer de las dos maneras.

    # Traemos los datos del request, asegurandonos que son numeros, sino, les asignamos
    # un valor por defecto:
    if request.GET.get('offset') == None or request.GET['offset'].isdigit() == False:
        offset = 0
    else:
        offset = request.GET.get('offset')
    if request.GET.get('limit') == None or request.GET['limit'].isdigit() == False:
        limit = 15
    else:
        limit = request.GET.get('limit')

    offset = int(offset)
    limit = int(limit)

    # Realizamos el request:
    aditional_params = {'limit': limit, 'offset': offset}
    params = PARAMS
    params.update(aditional_params)
    # NOTE: A los parametros de hash, api key y demás, sumamos limit y offset para paginación.
    res = requests.get(URL_BASE+ENDPOINT, params=params)

    comics = json.loads(res.text)
    # Obtenemos la lista de comics:
    comics_list = comics.get('data').get('results')

    # Filtramos la lista de comics y nos quedamos con lo que nos interesa:
    for comic in comics_list:
        if comic.get('prices')[0].get('price') != 0:
            id.append(comic.get('id'))
            description.append(comic.get('description'))
            title.append(comic.get('title'))
            prices.append(comic.get('prices')[0].get('price'))
            thumbnail.append(
                f"{comic.get('thumbnail').get('path')}/standard_xlarge.jpg")

    # NOTE: Construimos la tabla, concatenando en un string el código HTML:

    template = '''<div>
    <div style="height:90%; width:90%; overflow:auto;background:gray;">
        <table>'''

    for i in range(len(id)):
        if description[i] == None:
            desc = "<h3>Description Not Available<h3>"
        else:
            desc = description[i]

        if prices[i] == 0.00:
            # Con este condicional inhabilitamos la compra de los comics sin precio.
            price = "<h3>N/A<h3>"
            visibility = "hidden"
        else:
            price = prices[i]
            visibility = "visible"

        template += f'''
        <tr>
        <td>
            <img src="{thumbnail[i]}">
        </td>
        <td>    
            <h2>{title[i]}</h2><br><br>
            {desc}
        </td>
        <td><h2>U$S{price}</h2></td>
        <td>
            <form action="/e-commerce/purchased_item/" method="post" , style ="visibility: {visibility};">
                <label for="qty"><h3>Enter Quantity:</h3></label>
                <input type="number" id="qty" name="qty" min="0" max="15">
                <input type="submit" value="Buy" >
                <input type="text" name="id" value="{id[i]}" style="visibility: hidden">
                <input type="text" name="title" value="{title[i]}" style="visibility: hidden">
                <input type="text" name="thumbnail" value="{thumbnail[i]}" style="visibility: hidden">
                <input type="text" name="description" value="{description[i]}" style="visibility: hidden">
                <input type="text" name="prices" value="{prices[i]}" style="visibility: hidden">
            </form>
        </td>
        </tr>
        
        '''
    template += f'</table></div></div>'
    # Imprimimos por consola el HTML construido (se puede probar en https://codepen.io/):
    # print(template)
    # O lo podemos guardar en un HTML, como el nombre no cambia, el archivo se pisa en cada petición:
    f = open('get_comics.html','w')
    f.write(template)
    f.close
    return HttpResponse(template)


@csrf_exempt
def get_comics_by_titles(request):
    '''
    Vista personalizada de API para comprar comics x busqueda de titulo, 
    primero consultamos los comics disponibles en la página de Marvel, 
    luego generamos una lista de los que tienen precio y descripción, 
    porque varios vienen `null`.
    '''
    # Declaramos nuestras variables:
    id = []
    title = []
    description = []
    prices = []
    thumbnail = []
    limit = 0
    offset = 0

    # Traemos los datos del request, asegurandonos que son numeros, sino, les asignamos
    # un valor por defecto:
    if request.GET.get('offset') == None or request.GET['offset'].isdigit() == False:
        offset = 0
    else:
        offset = request.GET.get('offset')
    if request.GET.get('limit') == None or request.GET['limit'].isdigit() == False:
        limit = 15
    else:
        limit = request.GET.get('limit')

    offset = int(offset)
    limit = int(limit)

    # Realizamos el request:
    aditional_params = {'limit': limit, 'offset': offset}
    params = PARAMS
    params.update(aditional_params)
    param_busqueda = request.GET['title']
    parametro = '?title='
    res = requests.get(URL_BASE+ENDPOINT+parametro+param_busqueda, params=params)
    comics = json.loads(res.text)
    print(comics)
    # Obtenemos la lista de comics:
    comics_list = comics.get('data').get('results')

    # Filtramos la lista de comics y nos quedamos con lo que nos interesa:
    for comic in comics_list:
        if comic.get('prices')[0].get('price') != 0:
            id.append(comic.get('id'))
            description.append(comic.get('description'))
            title.append(comic.get('title'))
            prices.append(comic.get('prices')[0].get('price'))
            thumbnail.append(
                f"{comic.get('thumbnail').get('path')}/standard_xlarge.jpg")

    # NOTE: Construimos la tabla, concatenando en un string el código HTML:

    template = '''<div>
    <div style="height:90%; width:90%; overflow:auto;background:gray;">
        <table>'''

    for i in range(len(id)):
        if description[i] == None:
            desc = "<h3>Description Not Available<h3>"
        else:
            desc = description[i]

        if prices[i] == 0.00:
            # Con este condicional inhabilitamos la compra de los comics sin precio.
            price = "<h3>N/A<h3>"
            visibility = "hidden"
        else:
            price = prices[i]
            visibility = "visible"

        template += f'''
        <tr>
        <td>
            <img src="{thumbnail[i]}">
        </td>
        <td>    
            <h2>{title[i]}</h2><br><br>
            {desc}
        </td>
        <td><h2>U$S{price}</h2></td>
        <td>
            <form action="/e-commerce/purchased_item/" method="post" , style ="visibility: {visibility};">
                <label for="qty"><h3>Enter Quantity:</h3></label>
                <input type="number" id="qty" name="qty" min="0" max="15">
                <input type="submit" value="Buy" >
                <input type="text" name="id" value="{id[i]}" style="visibility: hidden">
                <input type="text" name="title" value="{title[i]}" style="visibility: hidden">
                <input type="text" name="thumbnail" value="{thumbnail[i]}" style="visibility: hidden">
                <input type="text" name="description" value="{description[i]}" style="visibility: hidden">
                <input type="text" name="prices" value="{prices[i]}" style="visibility: hidden">
            </form>
        </td>
        </tr>
        
        '''
    template += f'</table></div></div>'
    f = open('get_comics_by_titles.html','w')
    f.write(template)
    f.close
    return HttpResponse(template)


@csrf_exempt
def get_characters(request):
    '''
    Vista personalizada de API para comprar comics x busqueda de titulo, 
    primero consultamos los comics disponibles en la página de Marvel, 
    luego generamos una lista de los que tienen precio y descripción, 
    porque varios vienen `null`.
    '''
    # Declaramos nuestras variables:
    id = []
    name = []
    description = []
    thumbnail = []
    stories = []
    limit = 0
    offset = 0

    # Traemos los datos del request, asegurandonos que son numeros, sino, les asignamos
    # un valor por defecto:
    if request.GET.get('offset') == None or request.GET['offset'].isdigit() == False:
        offset = 0
    else:
        offset = request.GET.get('offset')
    if request.GET.get('limit') == None or request.GET['limit'].isdigit() == False:
        limit = 15
    else:
        limit = request.GET.get('limit')

    offset = int(offset)
    limit = int(limit)

    # Realizamos el request:
    aditional_params = {'limit': limit, 'offset': offset}
    params = PARAMS
    params.update(aditional_params)
    # param_busqueda = request.GET['title']
    # parametro = '?title='
    res = requests.get(URL_BASE+ENDPOINT_CHARACTER, params=params)
    comics = json.loads(res.text)
    # print('print get_characters ',  comics)
    # Obtenemos la lista de comics:
    comics_list = comics.get('data').get('results') 
    # Filtramos la lista de comics y nos quedamos con lo que nos interesa:
    for comic in comics_list:
        # if comic.get('prices')[0].get('price') != 0:
        id.append(comic.get('id'))
        description.append(comic.get('description'))
        name.append(comic.get('name'))
        stories_list = comic.get('stories')
        for storie in stories_list.get('items'):
            # print('storie ',storie['name'] )
            stories.append(storie['name'])
        # prices.append(comic.get('prices')[0].get('price'))
        try :
            thumbnail.append(
                f"{comic.get('thumbnail').get('path')}/standard_xlarge.jpg")
        except ImportError as exc:
            raise ImportError(
            "no existe imagen para este regisro"
        ) from exc

    # NOTE: Construimos la tabla, concatenando en un string el código HTML:

    template = '''<div>
    <div style="height:95%; width:95%; overflow:auto;background:gray;">
        <table>'''

    for i in range(len(id)):
        if description[i] == None:
            desc = "<h3>Description Not Available<h3>"
        else:
            desc = description[i]

        stories_list_tb = ''
        for item in stories[i]:
            stories_list_tb += item
        
        print(stories_list_tb)
        template += f'''
        <tr>
        <td>
            <img src="{thumbnail[i]}">
        </td>
        <td>    
            <h2>{name[i]}</h2><br><br>
            {desc}
        </td>
       
        <td>
        <h2> Stories </h2><br><br>
        <h3> {stories_list_tb} </h3>
        </td>
        <td>
                <input type="text" name="id" value="{id[i]}" style="visibility: hidden">
                <input type="text" name="title" value="{name[i]}" style="visibility: hidden">
                <input type="text" name="thumbnail" value="{thumbnail[i]}" style="visibility: hidden">
                <input type="text" name="description" value="{description[i]}" style="visibility: hidden">
                <input type="text" name="stories" value="stories " style="visibility: hidden"> 
        </td>
        </tr>
        
        '''
    template += f'</table></div></div>'
    f = open('get_characters.html','w')
    f.write(template)
    f.close
    return HttpResponse(template)

@csrf_exempt
def purchased_item(request):
    '''Incluye la lógica de guardar lo pedido en la base de datos 
    y devuelve el detalle de lo adquirido '''

    # Obtenemos los datos del request:
    title = request.POST.get('title')
    thumbnail = request.POST.get('thumbnail')
    description = request.POST.get('description')
    price = request.POST.get('prices')
    qty = request.POST.get('qty')
    id = request.POST.get('id')

    # TODO: Construimos la Query:
    # Verificamos que el comic no se encuentra en nuestro stock:

    queryset = Comic.objects.filter(marvel_id=id)

    if len(queryset.values_list()) == 0 :
        # Si el resultado nos trae una lista vacía, creamos un nuevo registro:
        item = Comic(title=title, description=description, price=price,
                    stock_qty=qty, picture=thumbnail, marvel_id=id)
        print(CIAN,queryset)
        item.save()
    else:
        # Si el comic está registrado, actualizamos su cantidad:
        comic = Comic.objects.get(marvel_id=id)
        actual_stock = comic.stock_qty
        actual_stock += int(qty)
        Comic.objects.filter(marvel_id=id).update(stock_qty=actual_stock)

    # NOTE: Construimos la respuesta
    # Calculamos el precio total:
    try:
        total = float(price) * int(qty)
    except:
        total = ". . ."
    # Creamos en una tabla la respuesta del comic comprado,
    # con precio unitario y precio total:
    template = f'''
    <h1>
    Your purchased product:
    </h1>
    <table>
    <tr>
        <td>
        <img src="{thumbnail}">
        </td>
        <td>
            <ul>
                <li><h2>{title}</h2></li>
                <li>ID: {id}</li>
                <li>Description: {description}</li>
                <li>Price (each): U$S{price}</li>
                <li>Qty.: {qty}</li>
                <li><h3>Total: U$S {total:.2f}</h3></li>
            </ul>
        </td>
    <tr>
    </table>
    '''
    # Imprimimos por consola el HTML construido (se puede probar en https://codepen.io/):
    print(VERDE+template)
    return HttpResponse(template)
