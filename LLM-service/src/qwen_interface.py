from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from src.request import post_request
from src.structs import MongoPayloadStruct,StoreContentStruct,RAGDocumentStruct
# from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.vllm import Vllm

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader



class Qwen:
    #Qwen sadly does not use the huggingfaces inbuilt rag integration, llama_index used for convenience
    #never used Qwen before this, lets see if its as good as the internet says it is
    #TODO: set reasonable VRAM usage param
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct-AWQ")

        self.sampling_params = SamplingParams(temperature=0.7, top_p=0.8, repetition_penalty=1.05, max_tokens=1024)

        # AWQ quantization, 3B params, because thats as high as my pc can handle
        # Deployed with Vllm
        Settings.llm = Vllm(model="Qwen/Qwen2.5-3B-Instruct-AWQ")

        # Qwens 1.5B instruct embedding model takes too much VRAM
        # bge base works with the available VRAM
        Settings.embed_model = HuggingFaceEmbedding(
            model_name = "BAAI/bge-base-en-v1.5"
        )
        Settings.transformations = [SentenceSplitter(chunk_size=1024)]

        self._inject_documents()

        self.index = self._create_index()
        self.messages = []

        self._construct_system_prompt()

        self.query_engine = self.index.as_query_engine()
    
    def _create_index(self):
        #create index for data to be accessed by llama index via rag
        documents = SimpleDirectoryReader("./src/docs").load_data()
        index = VectorStoreIndex.from_documents(
            documents,
            embed_model=Settings.embed_model,
            transformations=Settings.transformations
        )
        return index

    def _optimize_documents(self,documents):
        #TODO: redo RAG architecture, the current method cannot properly aggragate all stores together
        #TODO: mix tooling with RAG, that would allow for analysis
        #TODO: the locations are not obvious enough for the LLM, need more advanced geocoding
        #TODO: look into parsing in distance data between different shops into the documents
        #TODO: you shouldnt do this here, it is the responsiblity of scraping-service, or a dedicated seperate service
        cleaned_documents = []
        for item in documents:
            item["id"] = item["_id"]
            store = StoreContentStruct(**item)

            name_prompt = f"This store is called {' '.join(store.name.split())}"
            address_prompt = f",it is located at {' '.join(store.address.split(',')[-4:])}"
            full_address_prompt = f",its full address of the store is {' '.join(store.address.split())}"
            opening_hours = lambda x: " ".join(' and '.join(x).split()) #kek python magic, removes all whitespaces and preserve spaces between words, while joining the strings in list
            opening_times_prompt = f",and the opening hours of this store is {opening_hours(store.opening_times)}"

            document = RAGDocumentStruct(
                id=store.id,
                name=store.name,
                text=name_prompt+address_prompt+opening_times_prompt
            )
            cleaned_documents.append(document)
        
        return cleaned_documents
    
    def _inject_documents(self):
        #TODO: current implementation requires class reinitialization to get updated data
        #for rag, real implementation would require an endpoint for a schedule service to 
        #update the documents

        response = post_request(
            "/mongo",
            MongoPayloadStruct(
                collection="SandwichStores",
                operation="find_all",
                data = {},
            ).model_dump()
        )
        #TODO: no way to remove outdated ids
        documents = self._optimize_documents(response)
        with open(f"./src/docs/all_stores.txt","w") as file:
            file.write("the following is a list of all the stores in malaysia:\n\n")
            for docs in documents:

                content  = docs.model_dump()
                file.write(content["text"]+"\n")
            file.close()

        
    
    def _construct_system_prompt(self):
        prompt_file = open(
            "./src/prompts/system_prompt.txt","r"
            )
        self.messages.append(
            {
                "role": "system", 
                "content": str(prompt_file.read()) 
                }
            )
        prompt_file.close()
        
    def _append_user_prompt(self,user_prompt):
        self.messages.append({"role": "user", "content": user_prompt})

    def generate(self,prompt):
        self._append_user_prompt(prompt)
        text = self.tokenizer.apply_chat_template(
            self.messages,
            tokenize=False,
            add_generation_prompt=True
        )
        output = self.query_engine.query(text).response
        #long continuous conversations would lead it to hallucinate, we only let it focus on one prompt at a time
        self.messages = [self.messages[0]]
        return output

    