//Este script está como componente en los objetos: robot, cajas y pilas.


using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEditor;


public class ObjectMover : MonoBehaviour
{
    public string apiUrl = "http://127.0.0.1:5000/move";
    public Dictionary<string, GameObject> objects = new Dictionary<string, GameObject>();

    void Start()
    {   
        // Definir posiciones fijas para cada objeto
        DefineInitialPositions();

        // Inicializar posiciones de los objetos
        InitializeObjects();

        // Iniciar la generación de posiciones y la obtención de datos desde la API
        StartCoroutine(AutoMoveObjects());
    }

    void DefineInitialPositions()
    {
        objects = new Dictionary<string, GameObject>
        {
            { "dron(render)", GameObject.Find("dron(render)") },
        };
    }

    void InitializeObjects()
    {
        // Asignar posiciones iniciales fijas
        foreach (var item in objects)
        {
            if (item.Value != null)
            {
                item.Value.transform.position = new Vector3(0, 0, 0); // Inicia en posición (0, 0, 0)
            }
            else
            {
                Debug.LogWarning("GameObject not found: " + item.Key);
            }
        }
    }

    IEnumerator AutoMoveObjects()
    {
        using (UnityWebRequest putRequest = new UnityWebRequest(apiUrl, "PUT"))
        {
            // Si deseas enviar datos en el cuerpo de la solicitud, los añades aquí
            string jsonData = ""; // Aquí pones los datos que deseas enviar como JSON
            byte[] jsonToSend = new System.Text.UTF8Encoding().GetBytes(jsonData);
            putRequest.uploadHandler = new UploadHandlerRaw(jsonToSend);
            putRequest.downloadHandler = new DownloadHandlerBuffer();

            // Establecer el encabezado de la solicitud como 'application/json'
            putRequest.SetRequestHeader("Content-Type", "application/json");

            yield return putRequest.SendWebRequest();

            if (putRequest.result == UnityWebRequest.Result.ConnectionError || putRequest.result == UnityWebRequest.Result.ProtocolError)
            {
                // Manejar el error
                Debug.LogError(putRequest.error);
                yield return new WaitForSeconds(0.5f); // Consulta cada x tiempo
                
            }
            else
            {
                Debug.Log("PUT realizado exitosamente. Iniciando obtención de posiciones...");
            }
        }

        // (POST)
        using (UnityWebRequest postRequest = UnityWebRequest.PostWwwForm(apiUrl, ""))
        {
            yield return postRequest.SendWebRequest();

            if (postRequest.result == UnityWebRequest.Result.ConnectionError || postRequest.result == UnityWebRequest.Result.ProtocolError)
            {
                // Debug.LogError(postRequest.error);
                new WaitForSeconds(.5f); // Consulta cada x tiempo
                yield break;
            }
            else
            {
                Debug.Log("POST realizado exitosamente. Iniciando obtención de posiciones...");
            }
        }

        while (true)
        {
            // (GET)
            using (UnityWebRequest getRequest = UnityWebRequest.Get(apiUrl))
            {
                yield return getRequest.SendWebRequest();

                if (getRequest.result == UnityWebRequest.Result.ConnectionError || getRequest.result == UnityWebRequest.Result.ProtocolError)
                {
                    if (getRequest.responseCode == 404)
                    {
                        break;
                    }
                    else
                    {
                        Debug.LogError(getRequest.error);
                    }
                }
                else
                {
                    // Procesar la respuesta de la API
                    var json = getRequest.downloadHandler.text;
                    Debug.Log("JSON recibido: " + json);

                    // Usar JObject para analizar el JSON y verificar el tipo de datos
                    JObject jsonData = JObject.Parse(json);
                    Dictionary<string, float[]> data = new Dictionary<string, float[]>();

                    foreach (var item in jsonData)
                    {
                        if (item.Value is JArray)
                        {
                            // Convertir JArray a float[]
                            float[] positions = item.Value.ToObject<float[]>();
                            data.Add(item.Key, positions);
                        }
                        else
                        {
                            Debug.LogWarning($"Valor inesperado para la clave {item.Key}: {item.Value}");
                        }
                    }

                    // Actualizar posiciones en función de los datos recibidos
                    UpdateObjectPositions(data);
                }
            }

            yield return new WaitForSeconds(.5f); // Consulta cada x tiempo
        }
        
        QuitGame();

        // StopGameInEditor();
        // Application.Quit();
    }

    void QuitGame()
        {
            #if UNITY_EDITOR
                    EditorApplication.isPlaying = false; // Stops the game in the Unity Editor
            #else
                    Application.Quit(); // Quits the application in a standalone build
            #endif
        }
    void UpdateObjectPositions(Dictionary<string, float[]> data)
{
    foreach (var item in objects)
    {
        if (data.ContainsKey(item.Key))
        {
            Vector3 newPosition = new Vector3(data[item.Key][0], data[item.Key][1], data[item.Key][2]);
            item.Value.transform.position = newPosition;
        }
        else
        {
            Debug.LogWarning($"No data for {item.Key}. Moving to default position.");
            item.Value.transform.position = new Vector3(100, 0, 0); // Default if no data
        }
    }
}

}