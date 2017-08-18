from rest_framework.permissions import BasePermission, SAFE_METHODS



class IsOwnerOrReadOnly(BasePermission):

    message = 'You must be the owner of the object'

    my_safe_method = ['PUT']

    def has_permissions(self,request,view):
    	#logging to console
    	import logging
    	logger = logging.getLogger()
    	handler = logging.StreamHandler()
    	formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    	handler.setFormatter(formatter)
    	logger.addHandler(handler)
    	logger.setLevel(logging.DEBUG)
    	#logging to console
    	if request.method in self.my_safe_method:
    		logger.debug("has_permissions_inside_if")
    		logger.removeHandler(handler)
    		return False
    	logger.debug("has_permissions_outside_if")
    	logger.removeHandler(handler)
    	return False

    

    def has_object_permission(self, request,view,obj):
    	#logging to console
    	import logging
    	logger = logging.getLogger()
    	handler = logging.StreamHandler()
    	formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    	handler.setFormatter(formatter)
    	logger.addHandler(handler)
    	logger.setLevel(logging.DEBUG)
    	#logging to consolwwe
    	if request.method in SAFE_METHODS:
    		logger.debug("has_object_permissions_inside_if")
    		logger.removeHandler(handler)
    		return True
    	logger.debug("has_object_permissions_outside_if")
    	logger.removeHandler(handler)
    	return obj.user == request.user
    	

