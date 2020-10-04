from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from services.home_data_svc.base import HouseCanaryHomeDataSvc


class HomeDataViewSet(ViewSet):
    app_name = 'v1'

    @action(detail=False, methods=['get'])
    def unregistered_home_data(self, request):
        """
        Returns home data about homes for non-registered users.

        Expected Parameters:
            zip: a zip code,
            address: a street address,
            fields: normalized fields to include in the response.
        """
        # Good to validate zip and address with regex here
        # to avoid unnecessary API calls,
        # endpoints handling bad requests differently.
        zip_code = request.GET.get('zip')
        address = request.GET.get('address')
        expected_fields = request.GET.getlist('fields')
        home_data_svc = HouseCanaryHomeDataSvc(expected_fields=expected_fields, address=address, zip_code=zip_code)
        home_data_svc.build_home_data()
        return Response(data=home_data_svc.data)
