from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import ZkguPerson
from .websocket_utils import send_person_created, send_person_updated, send_person_deleted

def person_management_view(request):
    return render(request, 'zkgu_persons/index.html')

@csrf_exempt
@require_http_methods(["GET", "POST"])
def debug_persons(request):
    try:
        if request.method == 'GET':
            persons = list(ZkguPerson.objects.all().values())
            return JsonResponse({
                'status': 'success',
                'count': len(persons),
                'results': persons
            })
        elif request.method == 'POST':
            data = json.loads(request.body)
            person = ZkguPerson.objects.create(
                ID_REC=data.get('ID_REC'),
                LASTNAME=data.get('LASTNAME'),
                FIRSTNAME=data.get('FIRSTNAME', ''),
                MIDNAME=data.get('MIDNAME', '')
            )
            
            person_data = {
                'ID_REC': person.ID_REC,
                'LASTNAME': person.LASTNAME,
                'FIRSTNAME': person.FIRSTNAME,
                'MIDNAME': person.MIDNAME,
                'DELETION_MARK': person.DELETION_MARK,
                'last_update': person.last_update.isoformat() if person.last_update else None,
                'created_at': person.created_at.isoformat() if person.created_at else None,
            }
            
            send_person_created(person_data)
            
            return JsonResponse({
                'status': 'success',
                'data': person_data
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        })

@csrf_exempt
def delete_person(request, id_rec):
    """Удаление персоны"""
    try:
        person = ZkguPerson.objects.get(ID_REC=id_rec)
        
        person_data = {
            'ID_REC': person.ID_REC,
            'LASTNAME': person.LASTNAME,
            'FIRSTNAME': person.FIRSTNAME,
            'MIDNAME': person.MIDNAME,
            'DELETION_MARK': person.DELETION_MARK,
        }
        
        person.delete()
        
        send_person_deleted(person_data)
        
        return JsonResponse({'status': 'success'})
    except ZkguPerson.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Person not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)})

@csrf_exempt
def get_person(request, id_rec):
    try:
        person = ZkguPerson.objects.get(ID_REC=id_rec)
        return JsonResponse({
            'status': 'success',
            'data': {
                'ID_REC': person.ID_REC,
                'LASTNAME': person.LASTNAME,
                'FIRSTNAME': person.FIRSTNAME,
                'MIDNAME': person.MIDNAME,
                'DELETION_MARK': person.DELETION_MARK,
                'last_update': person.last_update.isoformat() if person.last_update else None,
                'created_at': person.created_at.isoformat() if person.created_at else None,
            }
        })
    except ZkguPerson.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Person not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)})

@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def update_person(request, id_rec):
    try:
        person = ZkguPerson.objects.get(ID_REC=id_rec)
        data = json.loads(request.body)
        
        if 'LASTNAME' in data:
            person.LASTNAME = data['LASTNAME']
        if 'FIRSTNAME' in data:
            person.FIRSTNAME = data['FIRSTNAME']
        if 'MIDNAME' in data:
            person.MIDNAME = data['MIDNAME']
        if 'DELETION_MARK' in data:
            person.DELETION_MARK = data['DELETION_MARK']
            
        person.save()
        
        person_data = {
            'ID_REC': person.ID_REC,
            'LASTNAME': person.LASTNAME,
            'FIRSTNAME': person.FIRSTNAME,
            'MIDNAME': person.MIDNAME,
            'DELETION_MARK': person.DELETION_MARK,
            'last_update': person.last_update.isoformat() if person.last_update else None,
            'created_at': person.created_at.isoformat() if person.created_at else None,
        }
        
        send_person_updated(person_data)
        
        return JsonResponse({
            'status': 'success',
            'data': person_data
        })
    except ZkguPerson.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Person not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)})