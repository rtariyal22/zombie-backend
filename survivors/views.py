import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_http_methods

from survivors.models import InfectionReport, Survivor
from resources.models import InventoryItem, Item

# TODO: Validate request data. If using fastapi, this can be done with
#  Pydantic models. I am skipping this for now but it is important to
#  validate the data before using it.
#  I would also move all the db queries to a crud interface like its done for
#  the trade_items view. This is a good practice to separate the business logic
#  from the database logic. I am skipping this for now but it is important to
#  separate the concerns. This applies to all the views.


@csrf_exempt
@require_POST
def register_survivor(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)
        survivor = Survivor.objects.create(
            name=data['name'],
            age=data['age'],
            gender=data['gender'],
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        inventory = data.get('inventory', [])
        inventory_items = []
        for entry in inventory:
            item = Item.objects.get(name=entry['item'])
            inventory_items.append(InventoryItem(
                survivor=survivor,
                item=item,
                quantity=entry['quantity']
            ))
        InventoryItem.objects.bulk_create(inventory_items)
        return JsonResponse({'message': 'Survivor registered', 'id': survivor.pk}, status=201)
    except KeyError as e:
        return JsonResponse({'error': f'Missing field: {str(e)}'}, status=400)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Invalid item in inventory'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['PATCH'])
def update_location(request: HttpRequest, survivor_id: int) -> JsonResponse:
    try:
        data = json.loads(request.body)
        survivor = Survivor.objects.get(id=survivor_id)
        survivor.latitude = data['latitude']
        survivor.longitude = data['longitude']
        survivor.save()
        return JsonResponse({'message': 'Location updated'}, status=200)
    except Survivor.DoesNotExist:
        return JsonResponse({'error': 'Survivor not found'}, status=404)
    except KeyError as e:
        return JsonResponse({'error': f'Missing field: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def report_infection(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)
        reporter_id = data.get("reporter_id")
        infected_id = data.get("infected_id")

        if not reporter_id:
            return JsonResponse({"error": "Missing 'reporter_id'"}, status=400)

        if reporter_id == infected_id:
            return JsonResponse({"error": "You cannot report yourself"}, status=400)

        reporter = Survivor.objects.get(id=reporter_id)
        reported = Survivor.objects.get(id=infected_id)

        # Prevent infected survivors from reporting others
        if reporter.is_infected:
            return JsonResponse({"error": "Infected survivors cannot report others"}, status=403)

        # Create the infection report (only once per reporter → reported)
        report, created = InfectionReport.objects.get_or_create(
            reporter=reporter,
            reported=reported
        )

        if not created:
            return JsonResponse({"message": "You have already reported this survivor"}, status=200)

        report_count = InfectionReport.objects.filter(reported=reported).count()
        if report_count >= 3:
            reported.is_infected = True
            reported.save()
        return JsonResponse({"message": "Report submitted"}, status=201)
    except Survivor.DoesNotExist:
        return JsonResponse({"error": "Survivor not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET'])
def profile(request: HttpRequest, survivor_id: int) -> JsonResponse:
    try:
        survivor = Survivor.objects.get(id=survivor_id)
        inventory_items = InventoryItem.objects.filter(
            survivor=survivor).select_related('item')
        inventory = [
            {
                "item": item.item.name,
                "quantity": item.quantity
            }
            for item in inventory_items
        ]
    except Survivor.DoesNotExist:
        return JsonResponse({"error": "Survivor not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    else:
        response = {
            'id': survivor.pk,
            'name': survivor.name,
            'age': survivor.age,
            'gender': survivor.gender,
            'latitude': survivor.latitude,
            'longitude': survivor.longitude,
            'inventory': inventory,
            'infected': survivor.is_infected,
        }
        return JsonResponse(response, status=200)
