import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods
from resources.interface import TradeService
from resources.exceptions import TradeError
from resources.forms import TradeForm


@csrf_exempt
@require_http_methods(['PATCH'])
def trade_items(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)
        form = TradeForm(data)
        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        trade = TradeService(
            survivor_a_id=form.cleaned_data['survivor_a'],
            survivor_b_id=form.cleaned_data['survivor_b'],
            items_a=form.cleaned_data['items_a'],
            items_b=form.cleaned_data['items_b'],
        )
        trade.execute()
    except TradeError as te:
        return JsonResponse({"error": str(te)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Trade completed"}, status=200)
