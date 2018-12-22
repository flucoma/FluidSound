Fluidsound{
	classvar <uris;
	classvar <parseFunc;
	classvar <>server;

	*parseJSON{|jsonStr|
		var parsed = jsonStr;
		var a,x;
		jsonStr.do({|char,pos|
			var inString = false;
			char.switch(
				$",{(jsonStr[pos-1]==$\ && inString).not.if({inString = inString.not})},
				${,{ if(inString.not){parsed[pos] = $(} },
				$},{ if(inString.not){parsed[pos] = $)} }
			)
		});
		^parsed.interpret;
	}

	*initClass{
		uris = (
		\BASE :  "http://localhost:8008/similarity",
		\SIMILAR:"/similar",
		\SIMILAR_FEATURE:"/similar_feature",
		\SOUND : "/sound?sound_id=%",
		\SOUND_ANALYSIS : "/analysis"
		);

		try{
				parseFunc = {|str| str.parseYAML}
		}{
				parseFunc = {|str| Fluidsound.parseJSON(str)};
		};
	}

	*uri{|uri_key,args|
		^(uris[\BASE] ++ uris[uri_key].format(args));
	}
}


FLReq{
	var <url, <filePath, <cmd;
	*new{|anUrl,params|
		^super.new.init(anUrl, params);
	}

	init{|anUrl, params, method="GET"|
		var paramsString, separator = "?";
		url = anUrl;
		filePath = PathName.tmp ++ "fs_" ++ UniqueID.next ++ ".txt";
		params = params?IdentityDictionary.new;
		params.postln;
		paramsString = params.keys(Array).collect({|k|
			k.asString ++ "=" ++ params[k].asString.urlEncode}).join("&");
		paramsString.postln;
		if (url.contains(separator)){separator = "&"};
		cmd = "curl  '%'>% ".format(this.url ++ separator ++ paramsString, filePath);
		cmd.postln;
	}

	get{|action, objClass|
		cmd.unixCmd({|res,pid|
			var result = objClass.new(
				File(filePath,"r").readAllString.postln;
				Fluidsound.parseFunc.value(
					File(filePath,"r").readAllString
				)
			);
			action.value(result);
		});
	}

}

FLObj : Object{
	var <dict;
	*new{|jsonDict|
		^super.new.init(jsonDict);
	}

	init{|jsonDict|
		dict = jsonDict.as(Dictionary);
		if (dict["error"].notNil && dict["error"]=="true" ){
			dict["result"].throw;
		};

		dict.keysDo{|k|
			this.addUniqueMethod(k.replace("-","_").asSymbol,{
				var obj = dict[k];
				if (obj.isKindOf(Dictionary)){obj=FLObj.new(obj)};
				obj;
			});
		};


	}
	at{|x| ^this.dict.at(x)}
}



FLList : FLObj {

	at{|i|
		this.result.results.size.postln;
		^FLSound.new(this.result.results[i]);
	}

	do{|f|
		this.dict.keys.postln;
		this.result.results.do({|snd,i| f.value( FLSound.new(snd))});
	}

}



FLSound : FLObj{


	*initParams{|params|
		if (params.isNil){params = ()};
		^params;
	}

	*getSound{|soundId, action|
		FLReq.new(
			Fluidsound.uri(\SOUND,soundId)).get(action, FLSound);
	}

	*contentSearch{|target, filter, action|
		var params = FLSound.initParams(params);
		var target_type, uri;
		target.class.name.postln;
		if ((target.asInt>0) || (target=="0")){
			uri = \SIMILAR;
		}{
			uri = \SIMILAR_FEATURE;
		};
		params.putAll(('target' : target, 'filter' : filter));
		FLReq.new(Fluidsound.uri(uri), params).get(action, FLList);
	}

	retrieve{|path, action|
			//sounds are local
			action.value;
	}

	previewFilename{|format = "wav"|
		^this.name.splitext[0]++"."++format;
	}

	retrievePreview{|path, action|
			action.value;
	}

	getSimilar{| action|
		var params=('target' : this["id"]);
		FLReq.new(Fluidsound.uri(\SIMILAR), params).get(action,FLList);
	}
	getAnalysis{|descriptors, action|
		var url = Fluidsound.uri(\SOUND_ANALYSIS,this["id"]);
		var params = ('sound_ids':this["id"]);
		if(descriptors.notNil){params.putAll(('descriptor_names' : descriptors))};
		FLReq.new(url,params).get(action,FLObj);
	}

}


+String{
	urlEncode{
		var str="";
		this.do({|c|
			if(c.isAlphaNum)
			{str = str++c}
			{str=str++"%"++c.ascii.asHexString(2)}
		})
		^str;
	}
}
