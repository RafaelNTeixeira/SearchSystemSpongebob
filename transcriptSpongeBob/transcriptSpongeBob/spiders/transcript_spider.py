import scrapy

class TranscriptSpider(scrapy.Spider):
    name = 'transcript'
    start_urls = ['https://spongebob.fandom.com/wiki/Help_Wanted/transcript'] # Alterar de acordo com o episódio

    def parse(self, response):
        ul_elements = response.css('div.mw-parser-output ul')

        for ul in ul_elements:
            li_elements = ul.css('li')

            for li in li_elements:
                character = li.css('b::text').get(default='').strip() # Nome do personagem a dialogar

                # Se recebe ':' como nome de personagem, significa que o nome da personagem está como hiperligação (<a>)
                if character == ':':
                    character = li.css('b a::text').get(default='').strip()
                    
                dialogue_parts = li.xpath('.//text()').getall() # Retira todos os nodes de texto, incluindo as tags <i>

                dialogue = ' '.join(part.strip() for part in dialogue_parts if part.strip()) # Retirar espaços em branco e juntar as partes do diálogo

                if dialogue:
                    print(f'{dialogue}')

        '''
        for text in ul_elements:
            li_texts = text.css('li::text').getall()

            for text in li_texts:
                print(text)
        '''

        '''
        # Caso se prefira um formato em comprehension lists
        transcripts = [[li.css('::text').getall() for li in ul.css('li')] for ul in ul_elements]

        for transcript in transcripts:
            for line in transcript:
                print(line)
        '''