# coding: utf-8
import tornado
import json
import uuid
from util.ApiConfiger import ApiConfig
from util.tool import need_auth
import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging
import traceback

class ServingHandler(tornado.web.RequestHandler):

    def parse(self, data):
        return json.loads(data)

    def genV1Service(self, uid):
        servingId = "tf-serving-"  + uid
        body = kubernetes.client.V1Service()
        body.api_version = "v1"
        body.kind = "Service"
        metaBody = kubernetes.client.V1ObjectMeta()
        metaBody.name = servingId
        body.metadata = metaBody
        specBody = kubernetes.client.V1ServiceSpec()
        specBody.selector = {"tf": servingId}
        rpcPortBody = kubernetes.client.V1ServicePort(port=ApiConfig().getint("k8s", "rpc_port"))
        rpcPortBody.name = "rpc"
        rpcPortBody.target_port = "rpc"
        httpPortBody = kubernetes.client.V1ServicePort(port=ApiConfig().getint("k8s", "http_port"))
        httpPortBody.name = "http"
        httpPortBody.target_port = "http"
        specBody.ports = [rpcPortBody, httpPortBody]
        body.spec = specBody
        return body

    def createService(self, uid, runInfo):
        authFile = ApiConfig().get("k8s", "auth_file")
        config.load_kube_config(authFile if authFile else None)
        configuration = kubernetes.client.Configuration()
        api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
        namespace = 'default'
        body = self.genV1Service(uid)
        print body
        logging.info("create service body: " + str(body))
        try:
            print '='*10 
            api_response = api_instance.create_namespaced_service(namespace, body)
            print api_response
            logging.info("service response: " + str(api_response))
            return api_response.spec.cluster_ip+":"+ApiConfig().get("k8s", "http_port")
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)
            logging.info("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)
            raise

    def genV1Rs(self, uid, modelParentPath, modelName):
        servingId = "tf-serving-" + uid
        body = kubernetes.client.V1ReplicaSet()
        body.api_version = "apps/v1"
        body.kind = "ReplicaSet"
        body.metadata = kubernetes.client.V1ObjectMeta()
        body.metadata.name = servingId
        labelSelector = kubernetes.client.V1LabelSelector()
        labelSelector.match_labels = {"tf": servingId}
        specBody = kubernetes.client.V1ReplicaSetSpec(selector=labelSelector)
        specBody.replicas = 1

        tempSpec = kubernetes.client.V1PodTemplateSpec()
        tempMetaBody = kubernetes.client.V1ObjectMeta()
        tempMetaBody.name = servingId
        tempMetaBody.labels = {"tf": servingId}
        tempSpec.metadata = tempMetaBody

        containerBody = kubernetes.client.V1Container(name=servingId)
        containerBody.image = ApiConfig().get("image", "serving")
        rpcPortBody = kubernetes.client.V1ContainerPort(container_port=ApiConfig().getint("k8s", "rpc_port"))
        rpcPortBody.name = "rpc"
        httpPortBody = kubernetes.client.V1ContainerPort(container_port=ApiConfig().getint("k8s", "http_port"))
        httpPortBody.name = "http"
        containerBody.ports = [rpcPortBody, httpPortBody]
        volMount = kubernetes.client.V1VolumeMount(mount_path="/models/"+modelName, name="glusterfsvol-"+uid)
        containerBody.volume_mounts = [volMount]
        envBody = kubernetes.client.V1EnvVar(name="MODEL_NAME", value=modelName)
        containerBody.env = [envBody]

        volBody = kubernetes.client.V1Volume(name="glusterfsvol-"+uid)
        # TODO mount model path
        parentPath = modelParentPath + "/" if modelParentPath else ""
        modelPath = "/" + parentPath + modelName
        gfsVol = kubernetes.client.V1GlusterfsVolumeSource(endpoints="glusterfs-cluster", path="gv1/good/"+self.basicUsername+modelPath)
        volBody.glusterfs = gfsVol

        tempInnerSpec = kubernetes.client.V1PodSpec(containers=[containerBody], volumes=[volBody])
        tempSpec.spec = tempInnerSpec
        specBody.template = tempSpec
        body.spec = specBody
        print body
        logging.info("rs body: " + str(body))
        return body


    def createRs(self, uid, info):
        configuration = kubernetes.client.Configuration()
        api_instance = kubernetes.client.AppsV1Api(kubernetes.client.ApiClient(configuration))
        namespace = ApiConfig().get("namespace", info.get("type", "tensorflow"))
        model = info.get("name", "test")
        modelParentPath = info.get("path", "/path")
        try:
            body = self.genV1Rs(uid, modelParentPath, model)
            api_response = api_instance.create_namespaced_replica_set(namespace, body)
        except ApiException as e:
            print("Exception when calling AppsV1Api->create_namespaced_replica_set: %s\n" % e)
            logging.error("Exception when calling AppsV1Api->create_namespaced_replica_set: %s\n" % e)
            raise

    def submit(self, info):
        uid = uuid.uuid1()
        svcAddr = self.createService(str(uid), info)
        self.createRs(str(uid), info)
        self.write('ready predict: ' + svcAddr)

    @need_auth
    @tornado.web.asynchronous
    def post(self):
        try:
            print "POST data: " + str(self.request.body)
            logging.info("POST data: " + str(self.request.body))
            info = self.parse(self.request.body)
            print "parse data: " + str(info)
            logging.info("parse data: " + str(info))
            self.submit(info)
        except:
            traceback.print_exc()
        self.finish()
