# This program is derived from the similarity_server of Freesound:
# https://github.com/MTG/freesound/tree/master/similarity
# (c) 2012-2018 MUSIC TECHNOLOGY GROUP, UNIVERSITAT POMPEU FABRA
# (c) 2018 UNIVERSITY OF HUDDERSFIELD
# You can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# https://www.gnu.org/licenses/agpl.html

from __future__ import print_function
import sys
from os.path import (
    basename,
    splitext,
    exists
)
from twisted.web import server, resource
from twisted.internet import reactor
from gaia_wrapper import GaiaWrapper
import settings
import messages
import logging
from similarity_server_utils import (
    parse_filter,
    parse_target,
    parse_metric_descriptors)
import json
import yaml
import pickle

def server_interface(resource):
    return {
        'add_point': resource.add_point,
        'save': resource.save,
        'descriptor_names': resource.get_descriptor_names,
        'analysis': resource.get_analysis,
        'similar': resource.get_similar,
        'similar_feature': resource.get_similar_feature,
        'sound': resource.get_sound,
    }

class FluidSoundServer(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        self.methods = server_interface(self)
        self.isLeaf = False
        self.gaia = GaiaWrapper()
        self.filenames = {}
        if exists(settings.FILENAME_INDEX):
            with open(settings.FILENAME_INDEX, "rb") as f:
                self.filenames = pickle.load(f)
        print(self.filenames, exists(settings.FILENAME_INDEX))
    def getChild(self, name, request):
        return self

    def fail(self, message, status = settings.BAD_REQUEST_CODE):
        return json.dumps({
            'error': True,
            'result': message,
            'status_code': status
        })

    def render_GET(self, request):
        return self.methods[request.prepath[1]](request=request, **request.args)

    def sound_dict(self, sound_id):
        return {
            "id": sound_id,
            "name": self.filenames[sound_id],
            "url": self.filenames[sound_id],
            "username": "local",
            "duration":0 #TODO
        }

    ############### API methods #######
    def add_point(self, request, location, sound_id):
        print(splitext(basename(location[0]))[0])
        self.filenames[sound_id[0]] = str(splitext(basename(location[0]))[0])
        print("adding "+self.filenames[sound_id[0]], sound_id)
        return json.dumps( self.gaia.add_point(location[0],sound_id[0]))

    def save(self, request, filename = None):
        with open(settings.FILENAME_INDEX, "wb") as handle:
            pickle.dump(self.filenames, handle)
        filename = filename[0] if filename is not None else settings.INDEX_NAME
        return json.dumps(self.gaia.save_index(filename))

    def get_sound(self, request, sound_id):
        if not sound_id[0] in self.filenames:
            return self.fail(messages.FILE_NOT_FOUND, settings.NOT_FOUND_CODE)
        else:
            snd_obj = self.sound_dict(sound_id[0])
            snd_obj.update({"error":False})
            return json.dumps(snd_obj)

    def get_descriptor_names(self, request):
        return json.dumps({
            'error': False,
            'result': self.gaia.descriptor_names
        })

    def get_analysis(self, request, sound_ids, descriptor_names=None,
                     normalization=[0], only_leaf_descriptors=[0]):
        kwargs = dict()
        if descriptor_names:
            kwargs['descriptor_names'] = [
                name for name in descriptor_names[0].split(',') if name
            ]
        kwargs['normalization'] = normalization[0] == '1'
        kwargs['only_leaf_descriptors'] = only_leaf_descriptors[0] == '1'
        return json.dumps(
            self.gaia.get_sounds_descriptors(sound_ids[0].split(','), **kwargs)
        )

    def get_similar(self, request, target, filter = None,
                    num_results = settings.N_RESULTS):
        try:
            target = int(target[0])
        except:
            return self.fail(messages.INVALID_SOUND_ID)
        r =  self.api_search(request, 'sound_id', target, filter, num_results)
        print(r)
        return self.api_search(request, 'sound_id', target, filter, num_results)

    def get_similar_feature(self, request, target, filter = None,
                    num_results = settings.N_RESULTS):
        try:
            target = parse_target(
                target[0].replace("'", '"'),
                self.gaia.descriptor_names['fixed-length']
            )
            if type(target) == str:
                return self.fail(target)
            elif type(target) != dict:
                return self.fail(messages.INVALID_DESC_VALS)
            if not target.items():
                return self.fail(messages.INVALID_TARGET)
        except Exception as e:
                    return self.fail(messages.INVALID_DESC_VALS)
        return self.api_search(
            request, 'descriptor_values', target, filter, num_results
        )

    def api_search(self, request, target_type = None, target = None,
                    filter = None, num_results = settings.N_RESULTS):
        if filter:
            try:
                result = parse_filter(
                    filter[0].replace("'", '"'),
                    self.gaia.descriptor_names['fixed-length']
                )
                if type(result) == str:
                    return self.fail( result)
                elif type(result) != list:
                    return self.fail(messages.INVALID_FILTER)
            except Exception as e:
                return self.fail(messages.INVALID_FILTER)

        if target_type == 'descriptor_values' and target:
            metric_descriptor_names = parse_metric_descriptors(
                                        ','.join(target.keys()),
                                        self.gaia.descriptor_names['fixed-length']
                                      )
        else:
            metric_descriptor_names = False

        result = self.gaia.api_search(target_type,
                                      target,
                                      filter,
                                      settings.DEFAULT_PRESET,
                                      metric_descriptor_names,
                                      num_results,
                                      0, # TODO
                                      None
                                      )
        parsed_results = []
        for r in range(len(result["result"]["results"])):
            sound_id = result["result"]["results"][r][0]
            if not sound_id in self.filenames:
                return self.fail(
                    messages.FILE_NOT_FOUND,
                    settings.NOT_FOUND_CODE
                )
            parsed_results.append(self.sound_dict(sound_id))
        result["result"]["results"] = parsed_results
        return json.dumps(result)

if __name__ == '__main__':
    logging.basicConfig(stream = sys.stdout, level = logging.DEBUG)
    logger = logging.getLogger('similarity')
    logger.info('Configuring similarity service...')
    root = resource.Resource()
    root.putChild("similarity", FluidSoundServer())
    site = server.Site(root)
    reactor.listenTCP(settings.PORT, site)
    logger.info('Started similarity service, listening to port ' + str(settings.PORT) + "...")
    reactor.run()
    logger.info('Service stopped.')
