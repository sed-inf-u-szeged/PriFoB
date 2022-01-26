package hu.sed.prifob

import android.content.Context
import android.util.Log
import org.json.JSONObject
import org.json.JSONTokener

class CredentialRepository (val context: Context) {

    fun getCredentials(): ArrayList<Credential>{
        var list: ArrayList<Credential> = ArrayList<Credential>()

        var files: Array<String> = context.fileList()

        for(file in files){
            Log.d("CredentialRepository", "file: " + file)
            var json: JSONObject = JSONObject(context.openFileInput(file).bufferedReader().use { it.readText() })
            var credJson:JSONObject = json.getJSONObject(Constants.CREDENTIAL)
            var did = credJson.getString(Constants.DID_IDENTIFIER)
            var schema = credJson.getString(Constants.SCHEMA_IDENTIFIER)
            var attributesJsonObject = credJson.getJSONObject(Constants.ATTRIBUTES)
            var attributes: HashMap<String, String> = HashMap()
            for (key in attributesJsonObject.keys()) {
                attributes.put(key, attributesJsonObject.getString(key))
            }
            list.add(Credential(file,  did, schema, attributes))
        }

        return list
    }

    fun saveCredential(credential: Credential, filename: String){
        var contentJson: JSONObject = JSONObject()
        var credentialJson: JSONObject = JSONObject()
        credentialJson.put(Constants.DID_IDENTIFIER, credential.institution)
        credentialJson.put(Constants.SCHEMA_IDENTIFIER, credential.profession)
        var attributesJson: JSONObject = JSONObject()
        for (key in credential.attributes.keys){
            attributesJson.put(key, credential.attributes.get(key))
        }
        credentialJson.put(Constants.ATTRIBUTES, credential.attributes)
        contentJson.put(Constants.CREDENTIAL, credentialJson)

        context.openFileOutput(filename, Context.MODE_PRIVATE).use {
            it.write(contentJson.toString().toByteArray())
        }
    }

    fun saveContent(content: String, filename: String){
        context.openFileOutput(filename, Context.MODE_PRIVATE).use {
            it.write(content.toByteArray())
        }
    }

}