
// Select the database to use.
use('binancedb');



db.pricep2psell.find(
  {advNo:"12653167801688666112", price:"13.30"}
)




db.pricep2psell.countDocuments()







db.pricep2psell.aggregate([
  {
    $group: {
      _id: { advNo: "$advNo", price: "$price" },
      ids: { $addToSet: "$_id" },
      count: { $sum: 1 }
    }
  },
  {
    $match: {
      count: { $gt: 1 }
    }
  }
]).forEach(function(doc) {
  doc.ids.shift(); // Mantén el primer ID y elimina los demás
  db.pricep2psell.deleteMany({ _id: { $in: doc.ids } });
});











db.pricep2psell.findOne({
  _id: ObjectId("66ac4a2b931fb8af357c6c19")
});





