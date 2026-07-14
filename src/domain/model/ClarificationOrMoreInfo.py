from pydantic import BaseModel, Field


class ClarificationOrMoreInfo(BaseModel):

     is_clarification: bool = Field(description="""
        Verdadero (True) si el usuario indica que NO ha entendido la respuesta anterior de la IA, 
        si muestra confusión, o pide que se le explique de forma más sencilla, clara o con otras palabras.
        Ejemplos que disparan True: 'No te entiendo', '¿A qué te refieres?', 'Explícamelo más fácil', 'No me queda claro'.
        """, default=False)
     is_more_info: bool = Field(description="""
      Verdadero (True) si el usuario sí entendió la respuesta anterior pero quiere profundizar, 
        pide más detalles, quiere ampliar la información con más ejemplos o datos adicionales sobre el mismo tema.
        Ejemplos que disparan True: 'Cuéntame más sobre eso', 'Dame un ejemplo de lo segundo', '¿Puedes ampliar este punto?'.
      """, default=False)
