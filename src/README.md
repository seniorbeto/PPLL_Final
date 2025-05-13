hay una única cosa que no he podido dejar igual a como lo teníamos en la práctica que entregamos y son los corchetes de los if, else y while. Tienen que ir seguidos. NO pueden tener antes un NEWLINE y no he conseguido solucionarlo sin que me de un warning de shift reduce



para el semántico
podemos elegir nosotros cómo hacerlo. hay que hacer una tabla de símbolos (normalmente en una clase aparte) que lleve un registro de todos los símbolos que se han estado declarando en el programa.
por ejemplo: 
TABLA: 
{
x: int
abcd: bool
pinga: vector(int, 4) 
}

hay estructuras (como se pone en el vector) que es necesario almacenar en la tabla de símbolos con argumentos adicionales (para el vector por ejemplo, hay que almacenar también su tamaño y el tipo de dato que contiene)

Es bastante correcto tener una clase por cada tipo de dato, es decir, tener una clase vector que represente a una variable de tipo vector, cuyos argumentos sean su tipo de dato y su longitud
Lo mismo para los registros y funciones, que tienen que tener sus argumentos, sus atributos, sus variables....


los registros se almacenan en una tabla distinta (tabla de registros) pero que viene a ser lo mismo 
por ejemplo, en la tabla de registros: 
REGISTROS
{
POINT: [(x, int), (y, int)]
}

TABLA DE SIMBOLOS
{
p: point,
x: int
}

para tener el scope en cuenta tenemos que apañarlos la vida, puede ser por ejemplo, un atributo de la clase Symbol
por ejemplo, si se declara una variable dentro de una función su scope será el ID de la función en donde se ha declarado. Si se trata de usar fuera, el scope sería "global", por lo que no estaría permitido su uso. De ahí viene el error. "Variable x is out of scope"