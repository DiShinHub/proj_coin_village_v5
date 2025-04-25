
import requests

class WebParser():

    def __init__(self):
        self.url_israel_palestine = "https://israelpalestine.liveuamap.com/"
        self.url_ukraine_russia = "https://liveuamap.com/"
        self.url_usa = "https://usa.liveuamap.com/"

    def request_get(self, url):

        try:

            response = requests.get(url)

            if response.status_code == 200:
                return response
            
            else:
                print("Failed to retrieve data from the website.")
                # TODO :raise
                
        except Exception as e:
            print(e)
            # TODO :raise

    def get_liveuamap(self, url):

        text_bundle = ""
        response = self.request_get(url)

        if not response:
            print("no res in ip")
            return text_bundle

        # start point
        sp = response.text.find('id="feedler"')
        if sp<0: return text_bundle
        text_response = response.text[sp:]
        
        for i in range(0,4):

            # parse core text
            point_text = ""

            sp = text_response.find('class="time top-info"')
            if sp<0: return text_bundle
            text_response = text_response[sp:]

            sp = text_response.find('class="title')
            if sp<0: return text_bundle
            text_response = text_response[sp:]

            ep = text_response.find('</div>')
            if sp<0: return text_bundle
            point_text = text_response[len('class="title')+2:ep]

            text_bundle += f"{point_text} \n\n"
        
        return text_bundle

    def get_coinness(self):

        url = "https://coinness.com/"

        text_bundle = ""
        response = self.request_get(url)

        if not response:
            print("no res in ip")
            return text_bundle
            
        return
    
    def get_kimpga(self):

        url = "https://kimpga.com/"
        text_bundle = ""
        response = self.request_get(url)

        if not response:
            print("no res in ip")
            return text_bundle
        
        text = response.text
        print(text)