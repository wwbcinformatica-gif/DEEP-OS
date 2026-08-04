function calcularSoma(a, b) {
  const resultado = a + b;
  if (resultado > 10) {
    console.log('Resultado é maior que 10:', resultado);
    return true;
  } else {
    console.log('Resultado é menor ou igual a 10:', resultado);
    return false;
  }
}

const usuarios = [
  { nome: 'João', idade: 30 },
  { nome: 'Maria', idade: 25 },
  { nome: 'Pedro', idade: 40 },
];

const filtrados = usuarios
  .filter(function (u) {
    return u.idade > 25;
  })
  .map(function (u) {
    return u.nome;
  });

const config = { host: 'localhost', port: 3000, debug: true, options: { timeout: 5000, retry: 3 } };

class Animal {
  constructor(nome, tipo) {
    this.nome = nome;
    this.tipo = tipo;
  }
  falar() {
    return `Olá, eu sou ${this.nome} e sou um ${this.tipo}`;
  }
}
