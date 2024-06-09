/*

## PROJETO SISTEMAS DISTRIBUIDOS - Prof. Calebe ##

INTEGRANTES:

Aline Stolai - RA: 22.121.003-2
Gian Malheiros Braga - RA: 22.121.054-5
João Lucas Freitas de Almeida Rocha - RA: 22.121.004-0
Lucca Kirsten da Costa - RA: 22.121.121-2

##################################################
*/

import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.io.*;
import java.math.BigInteger;

//Bibliotecas
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.util.DefaultPrettyPrinter;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;


public class Server {
    //initialize socket and input stream
    private ServerSocket server = null;
    private String DatabasePath = "./database/";

    // constructor with port
    public Server(int port) {
        // starts server and waits for a connection
        try {
            server = new ServerSocket(port);
            System.out.println("Server started");

            //Keep listening for a client request.
            while (true) {
                Socket socket = server.accept(); 
                SendResponse(socket);
            }

        } catch (IOException i) {
            System.out.println(i);
        }
    }

    private void SendResponse(Socket socket) {
        try {
            System.out.println("Client accepted");

            DataInputStream in = GetStreamSocket(socket);
            DataOutputStream out = new DataOutputStream(socket.getOutputStream());    

            System.out.println(String.format("[CLIENT IP] %s", socket.getInetAddress().getHostAddress()));

            String line = "";

            // reads message from client until "Over" is sent
            while (!line.equals("Over"))
            {
                try
                {
                    String raw_request = in.readUTF();

                    System.out.println(String.format("[SERVER] RAW DATA: '%s'", raw_request));

                    String response = "";
        
                    //Parse Client response (json)
                    JsonNode ParseRequest = (new ObjectMapper()).readTree(raw_request);
                    ObjectMapper prod_mapper = new ObjectMapper();
                    
                    switch (ParseRequest.get("processo").asText()) {
                        case "comprar":
                            ServerInfoMessage("Process: Comprar");
                            //create json para adicionar ao extrato.
                            String Username = ParseRequest.get("usuario").asText("undefined");
                            //read json produtos
                            JsonNode JsonProdutos = prod_mapper.readTree(ReadFileFromFolder("produtos.json"));

                            //write json results
                            ObjectMapper res_mapper = new ObjectMapper();
                            ObjectNode ResultRootNode = res_mapper.createObjectNode();

                            ArrayNode ArrayResultCompra = res_mapper.createArrayNode();
                            List<String> Extrato = new ArrayList<String>();

                            boolean IsUpdated = false;

                            //read json produtos + Obter atributos de cada produto.
                            for (JsonNode buy_elem : ParseRequest.get("compra")) {
                                Integer compra_ID = buy_elem.get("id").asInt(-1);
                                Integer compra_qtd = buy_elem.get("quantidade").asInt(0);
        
                                //encontrou ID?
                                boolean matchID = false;

                                ObjectNode compra_res = res_mapper.createObjectNode();
                                compra_res.put("id", compra_ID);
                                compra_res.put("status", "sucesso");
                                compra_res.put("descricao", "Compra realizada!");

                                String productName = "undefined";
                                for (JsonNode node : JsonProdutos) {
                                    if (node.get("id").asInt(-1) != compra_ID) continue;    
                                    matchID = true;

                                    productName = node.get("nome").asText("undefined");

                                    //verifica quantidade
                                    Integer prod_qtd = node.get("estoque").asInt(0);

                                    Integer sub = prod_qtd - compra_qtd;

                                    //se true, sem estoque.
                                    if (sub < 0) {
                                        compra_res.put("status", "erro_sem_estoque");
                                        compra_res.put("descricao", "Produto sem estoque!");
                                        break;
                                    }

                                    //atualizar node: man q locura parece python wtf
                                    ((ObjectNode) node).put("estoque", sub);
                                    IsUpdated = true;
                                }

                                if (!matchID) {
                                    compra_res.put("status", "erro_nao_encontrado");
                                    compra_res.put("descricao", "Produto ID não encontrado!");
                                }

                                //Build Extrato format
                                Extrato.add(
                                    String.format("[%s] user-%s: [%02d]\"%s\" %03d (status: %s)", 
                                        new Date().toInstant().toString(), 
                                        Username,
                                        compra_ID,
                                        productName,
                                        compra_qtd,
                                        compra_res.get("status").asText("undefined")
                                    )
                                );

                                ArrayResultCompra.add(compra_res);
                                //System.out.println(JsonProdutos.toPrettyString());
                            }

                            WriteToExtratoFile(Extrato);
                            ResultRootNode.set("resultado", ArrayResultCompra);
                            //! UPDATE results
                            String resultJSON = "{}";
                            try {
                                resultJSON = res_mapper.writerWithDefaultPrettyPrinter().writeValueAsString(ResultRootNode);
                                response = resultJSON;
                            } catch (JsonProcessingException e) {
                                e.printStackTrace();
                            } 

                            //atualiza produtos por inteiro.
                            if (IsUpdated) {
                                WriteJSONToFile("produtos.json", JsonProdutos);
                            }
                        break;
        
                        //Envia lista de produtos
                        case "sincronizar":
                            ServerInfoMessage("Process: Sincronizar");
                            response = "\n================================\n";
                            JsonNode JsonListProdutos = prod_mapper.readTree(ReadFileFromFolder("produtos.json"));
                            for (JsonNode node : JsonListProdutos) {
                                String p_name = node.get("nome").asText("undefined");
                                Integer p_id = node.get("id").asInt(-1);
                                Integer p_stock = node.get("estoque").asInt(0);
                                
                                String Build = String.format("[%d] \"%s\" | Estoque: %d\n", p_id, p_name, p_stock);

                                response += Build;
                            }
                            response += "================================\n";
                        break;  
        
                        //Envia extrato
                        case "extrato":
                            ServerInfoMessage("Process: Extrato");

                            response = ReadFileFromFolder("extrato.txt");
                        break;    
        
                        default:
                            ServerInfoMessage("Process: Desconhecido");
                        break;
                    }                

                    //TimeUnit.MILLISECONDS.sleep(2500);
                    writeLongUTF(out, response);
                    //System.out.println(response);
                }
                catch(IOException i)
                {
                    // i.printStackTrace();
                    // System.out.println(i);
                    break;
                }
            }

            // Close the streams and socket
            synchronized (this) {
                in.close();
                socket.close();
            }
        } catch (Exception e) {
            //WTF
            e.printStackTrace();
        }
    }

    private synchronized DataInputStream GetStreamSocket(Socket socket) throws IOException {
        return new DataInputStream(new BufferedInputStream(socket.getInputStream()));
    }

    private void ServerInfoMessage(String msg) {
        System.out.println("[INFO] " + msg);
    }

    //Supports Writting 4GB of data...
    public void writeLongUTF(DataOutputStream out, String str) throws IOException {

        byte[] utfBytes = str.getBytes(StandardCharsets.UTF_8);
        int length = utfBytes.length;
        byte[] lengthBytes = BigInteger.valueOf(length).toByteArray();

        // Ensure lengthBytes is exactly 4 bytes long
        byte[] paddedLengthBytes = new byte[4];
        System.arraycopy(lengthBytes, 0, paddedLengthBytes, 4 - lengthBytes.length, lengthBytes.length);

        out.write(paddedLengthBytes);  // Write the N-byte length prefix
        out.write(utfBytes);           // Write the UTF-8 bytes
    }

    private void WriteToExtratoFile(List<String> extratoList) throws NoSuchFileException {
        String ExtratoFull = "";
        for (int i=0; i<extratoList.size(); i++) {
            ExtratoFull += extratoList.get(i) + "\r\n";
        }

        WriteFileFromFolder("extrato.txt", ExtratoFull);
    }

    //Read from file in UTF-8 format
    private synchronized String ReadFileFromFolder(String filename) throws NoSuchFileException {
        try {
            File myObj = new File(DatabasePath + filename);
            if (!myObj.exists()) throw new NoSuchFileException(filename);

            BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(myObj), "UTF-8"));         
            StringBuilder data = new StringBuilder();
            String buffer = "";
            while ((buffer = br.readLine()) != null) {
                data.append(buffer);
            }
            br.close();

            return data.toString();
          } catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
          }
        throw new NoSuchFileException(filename);
    }
    
    //Write from file in UTF-8 format
    private synchronized static void WriteFileFromFolder(String filename, String str) throws NoSuchFileException {
        try {
            File myObj = new File("./database/" + filename);
            if (!myObj.exists()) {
                throw new NoSuchFileException(filename);
            };        
                
            BufferedWriter out = Files.newBufferedWriter(myObj.toPath(), StandardCharsets.UTF_8, StandardOpenOption.APPEND, StandardOpenOption.CREATE);

            out.write(str);
            out.close();
            return;
        } catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }
        throw new NoSuchFileException(filename);
    }

    private synchronized void WriteJSONToFile(String filename, JsonNode root_node) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        ObjectWriter writer = mapper.writer(new DefaultPrettyPrinter());
        writer.writeValue(new File(DatabasePath + filename), root_node);
        ServerInfoMessage("JSON-Writer: " + filename + " foi atualizado!");
    }

    public static void main(String args[]) {
        new Server(5000);
    }
}