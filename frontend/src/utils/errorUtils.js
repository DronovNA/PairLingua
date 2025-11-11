export function getErrorMessage(err) {
  if (!err) return "Неизвестная ошибка";
  if (typeof err === "string") return err;
  if (err.message) return err.message;

  // Пример обработки ошибки с массивом detail
  if (
    err.response &&
    err.response.data &&
    Array.isArray(err.response.data.detail)
  ) {
    const arr = err.response.data.detail;
    // собрать все сообщения ошибок в одну строку
    return arr.map(e => e.msg || JSON.stringify(e)).join('; ');
  }

  if (
    err.response &&
    err.response.data &&
    typeof err.response.data.detail === "string"
  ) {
    return err.response.data.detail;
  }

  return JSON.stringify(err);
}
